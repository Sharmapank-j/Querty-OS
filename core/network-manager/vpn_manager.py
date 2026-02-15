"""
VPN connection management for Querty-OS.
Handles VPN configuration, connection lifecycle, and routing.
"""

import logging
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from core.exceptions import NetworkConfigError, NetworkError

logger = logging.getLogger(__name__)


class VPNProtocol(Enum):
    """Supported VPN protocols."""

    OPENVPN = "openvpn"
    WIREGUARD = "wireguard"
    IPSEC = "ipsec"
    L2TP = "l2tp"
    PPTP = "pptp"


class VPNState(Enum):
    """VPN connection state."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"


@dataclass
class VPNConfig:
    """VPN configuration."""

    name: str
    protocol: VPNProtocol
    server: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    config_file: Optional[str] = None
    certificate_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_file: Optional[str] = None
    auto_reconnect: bool = True
    split_tunnel: bool = False
    dns_servers: Optional[List[str]] = None


@dataclass
class VPNConnection:
    """Active VPN connection."""

    config: VPNConfig
    state: VPNState
    interface: Optional[str] = None
    local_ip: Optional[str] = None
    remote_ip: Optional[str] = None
    connected_at: Optional[float] = None
    bytes_sent: int = 0
    bytes_received: int = 0
    process_id: Optional[int] = None
    error_message: Optional[str] = None


class VPNManager:
    """VPN connection manager."""

    def __init__(self, config_dir: str = "/data/vpn-configs"):
        """
        Initialize VPN manager.

        Args:
            config_dir: Directory for VPN configurations
        """
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, VPNConfig] = {}
        self.connections: Dict[str, VPNConnection] = {}

        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized VPNManager with config dir: {config_dir}")
        except Exception as e:
            raise NetworkConfigError(
                f"Failed to create config directory: {e}",
                error_code="CONFIG_DIR_FAILED",
                details={"path": config_dir},
            )

    def add_config(self, config: VPNConfig) -> bool:
        """
        Add VPN configuration.

        Args:
            config: VPNConfig to add

        Returns:
            True if successful, False otherwise

        Raises:
            NetworkConfigError: If config already exists
        """
        if config.name in self.configs:
            raise NetworkConfigError(
                f"VPN config already exists: {config.name}",
                error_code="CONFIG_EXISTS",
                details={"name": config.name},
            )

        # Validate config
        if not config.server:
            raise NetworkConfigError(
                "VPN server is required", error_code="INVALID_CONFIG", details={"name": config.name}
            )

        if config.protocol == VPNProtocol.OPENVPN and not config.config_file:
            logger.warning(f"OpenVPN config without config file: {config.name}")

        self.configs[config.name] = config
        logger.info(f"Added VPN config: {config.name} ({config.protocol.value})")
        return True

    def remove_config(self, name: str) -> bool:
        """
        Remove VPN configuration.

        Args:
            name: Config name

        Returns:
            True if removed, False if not found
        """
        if name not in self.configs:
            logger.warning(f"VPN config not found: {name}")
            return False

        # Disconnect if currently connected
        if name in self.connections:
            self.disconnect(name)

        del self.configs[name]
        logger.info(f"Removed VPN config: {name}")
        return True

    def get_config(self, name: str) -> Optional[VPNConfig]:
        """
        Get VPN configuration.

        Args:
            name: Config name

        Returns:
            VPNConfig or None if not found
        """
        return self.configs.get(name)

    def list_configs(self) -> List[VPNConfig]:
        """
        List all VPN configurations.

        Returns:
            List of VPNConfig objects
        """
        return list(self.configs.values())

    def connect(self, name: str, timeout: int = 30) -> VPNConnection:
        """
        Connect to VPN.

        Args:
            name: Config name
            timeout: Connection timeout in seconds

        Returns:
            VPNConnection object

        Raises:
            NetworkError: If connection fails
        """
        if name not in self.configs:
            raise NetworkConfigError(
                f"VPN config not found: {name}",
                error_code="CONFIG_NOT_FOUND",
                details={"name": name},
            )

        config = self.configs[name]

        # Check if already connected
        if name in self.connections:
            conn = self.connections[name]
            if conn.state == VPNState.CONNECTED:
                logger.info(f"Already connected to VPN: {name}")
                return conn
            elif conn.state == VPNState.CONNECTING:
                logger.info(f"Connection in progress: {name}")
                return conn

        # Create connection object
        connection = VPNConnection(config=config, state=VPNState.CONNECTING)
        self.connections[name] = connection

        try:
            # Connect based on protocol
            if config.protocol == VPNProtocol.OPENVPN:
                self._connect_openvpn(connection)
            elif config.protocol == VPNProtocol.WIREGUARD:
                self._connect_wireguard(connection)
            else:
                raise NetworkError(
                    f"VPN protocol not implemented: {config.protocol}",
                    error_code="PROTOCOL_NOT_IMPLEMENTED",
                    details={"protocol": config.protocol.value},
                )

            # Wait for connection
            start_time = time.time()
            while time.time() - start_time < timeout:
                if connection.state == VPNState.CONNECTED:
                    logger.info(f"Successfully connected to VPN: {name}")
                    return connection
                elif connection.state == VPNState.ERROR:
                    raise NetworkError(
                        f"VPN connection failed: {connection.error_message}",
                        error_code="CONNECTION_FAILED",
                        details={"name": name},
                    )
                time.sleep(1)

            # Timeout
            connection.state = VPNState.ERROR
            connection.error_message = "Connection timeout"
            raise NetworkError(
                f"VPN connection timeout: {name}",
                error_code="CONNECTION_TIMEOUT",
                details={"timeout": timeout},
            )

        except Exception as e:
            connection.state = VPNState.ERROR
            connection.error_message = str(e)
            logger.error(f"VPN connection failed: {e}")
            raise

    def _connect_openvpn(self, connection: VPNConnection) -> None:
        """
        Connect using OpenVPN.

        Args:
            connection: VPNConnection to establish
        """
        config = connection.config

        if not config.config_file:
            raise NetworkConfigError(
                "OpenVPN requires config file",
                error_code="MISSING_CONFIG_FILE",
                details={"name": config.name},
            )

        config_path = Path(config.config_file)
        if not config_path.exists():
            raise NetworkConfigError(
                f"Config file not found: {config.config_file}",
                error_code="CONFIG_FILE_NOT_FOUND",
                details={"path": config.config_file},
            )

        cmd = ["openvpn", "--config", str(config_path), "--daemon"]

        if config.username and config.password:
            # Create auth file
            auth_file = self.config_dir / f"{config.name}.auth"
            auth_file.write_text(f"{config.username}\n{config.password}\n")
            auth_file.chmod(0o600)
            cmd.extend(["--auth-user-pass", str(auth_file)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
            connection.state = VPNState.CONNECTING
            logger.info(f"Started OpenVPN connection: {config.name}")

            # In real implementation, would parse output for interface and IPs
            connection.interface = "tun0"

            # Simulate connection success for now
            time.sleep(2)
            connection.state = VPNState.CONNECTED
            connection.connected_at = time.time()

        except subprocess.CalledProcessError as e:
            raise NetworkError(
                f"OpenVPN failed: {e.stderr}",
                error_code="OPENVPN_FAILED",
                details={"stderr": e.stderr},
            )
        except FileNotFoundError:
            raise NetworkError("OpenVPN not installed", error_code="OPENVPN_NOT_FOUND")

    def _connect_wireguard(self, connection: VPNConnection) -> None:
        """
        Connect using WireGuard.

        Args:
            connection: VPNConnection to establish
        """
        config = connection.config

        if not config.config_file:
            raise NetworkConfigError(
                "WireGuard requires config file",
                error_code="MISSING_CONFIG_FILE",
                details={"name": config.name},
            )

        config_path = Path(config.config_file)
        if not config_path.exists():
            raise NetworkConfigError(
                f"Config file not found: {config.config_file}",
                error_code="CONFIG_FILE_NOT_FOUND",
                details={"path": config.config_file},
            )

        interface = f"wg-{config.name}"

        try:
            # Bring up WireGuard interface
            subprocess.run(
                ["wg-quick", "up", str(config_path)],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )

            connection.interface = interface
            connection.state = VPNState.CONNECTED
            connection.connected_at = time.time()
            logger.info(f"Started WireGuard connection: {config.name}")

        except subprocess.CalledProcessError as e:
            raise NetworkError(
                f"WireGuard failed: {e.stderr}",
                error_code="WIREGUARD_FAILED",
                details={"stderr": e.stderr},
            )
        except FileNotFoundError:
            raise NetworkError("WireGuard not installed", error_code="WIREGUARD_NOT_FOUND")

    def disconnect(self, name: str) -> bool:
        """
        Disconnect from VPN.

        Args:
            name: Config name

        Returns:
            True if disconnected, False if not connected
        """
        if name not in self.connections:
            logger.warning(f"Not connected to VPN: {name}")
            return False

        connection = self.connections[name]
        config = connection.config

        try:
            connection.state = VPNState.DISCONNECTING

            # Disconnect based on protocol
            if config.protocol == VPNProtocol.OPENVPN:
                self._disconnect_openvpn(connection)
            elif config.protocol == VPNProtocol.WIREGUARD:
                self._disconnect_wireguard(connection)

            connection.state = VPNState.DISCONNECTED
            del self.connections[name]
            logger.info(f"Disconnected from VPN: {name}")
            return True

        except Exception as e:
            connection.state = VPNState.ERROR
            connection.error_message = str(e)
            logger.error(f"Failed to disconnect VPN: {e}")
            return False

    def _disconnect_openvpn(self, connection: VPNConnection) -> None:
        """
        Disconnect OpenVPN connection.

        Args:
            connection: VPNConnection to disconnect
        """
        if connection.process_id:
            try:
                subprocess.run(["kill", str(connection.process_id)], check=False, timeout=5)
            except Exception as exc:
                logger.debug(
                    "Failed to kill OpenVPN process %s: %s",
                    connection.process_id,
                    exc,
                )

        # Alternative: kill all openvpn processes (not recommended in production)
        # subprocess.run(["killall", "openvpn"], check=False, timeout=5)

    def _disconnect_wireguard(self, connection: VPNConnection) -> None:
        """
        Disconnect WireGuard connection.

        Args:
            connection: VPNConnection to disconnect
        """
        config = connection.config
        if config.config_file:
            try:
                subprocess.run(
                    ["wg-quick", "down", config.config_file],
            except Exception as exc:
                logger.debug(
                    "Failed to bring down WireGuard interface with config %s: %s",
                    config.config_file,
                    exc,
                )
                    timeout=10,
                )
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                pass

    def get_connection(self, name: str) -> Optional[VPNConnection]:
        """
        Get active VPN connection.

        Args:
            name: Config name

        Returns:
            VPNConnection or None if not connected
        """
        return self.connections.get(name)

    def list_connections(self) -> List[VPNConnection]:
        """
        List all active VPN connections.

        Returns:
            List of VPNConnection objects
        """
        return list(self.connections.values())

    def get_connection_stats(self, name: str) -> Optional[Dict[str, int]]:
        """
        Get connection statistics.

        Args:
            name: Config name

        Returns:
            Dictionary with bytes_sent and bytes_received, or None
        """
        connection = self.connections.get(name)
        if not connection or connection.state != VPNState.CONNECTED:
            return None

        # In real implementation, would read from /sys/class/net/{interface}/statistics/
        return {"bytes_sent": connection.bytes_sent, "bytes_received": connection.bytes_received}

    def reconnect(self, name: str) -> VPNConnection:
        """
        Reconnect to VPN.

        Args:
            name: Config name

        Returns:
            VPNConnection object

        Raises:
            NetworkError: If reconnection fails
        """
        self.disconnect(name)
        time.sleep(1)
        return self.connect(name)

    def disconnect_all(self) -> int:
        """
        Disconnect all VPN connections.

        Returns:
            Number of connections disconnected
        """
        names = list(self.connections.keys())
        count = 0
        for name in names:
            if self.disconnect(name):
                count += 1
        logger.info(f"Disconnected {count} VPN connections")
        return count

    def is_connected(self, name: str) -> bool:
        """
        Check if VPN is connected.

        Args:
            name: Config name

        Returns:
            True if connected, False otherwise
        """
        connection = self.connections.get(name)
        return connection is not None and connection.state == VPNState.CONNECTED
