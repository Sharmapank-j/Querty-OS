"""
iptables-based firewall control for per-app network management.
Provides granular network access control for applications.
"""

import logging
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

from core.exceptions import NetworkError

logger = logging.getLogger(__name__)


class FirewallAction(Enum):
    """Firewall rule actions."""

    ACCEPT = "ACCEPT"
    DROP = "DROP"
    REJECT = "REJECT"
    LOG = "LOG"


class Protocol(Enum):
    """Network protocols."""

    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ALL = "all"


class Chain(Enum):
    """iptables chains."""

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    FORWARD = "FORWARD"


@dataclass
class FirewallRule:
    """Represents a firewall rule."""

    rule_id: str
    chain: Chain
    action: FirewallAction
    protocol: Optional[Protocol] = None
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    source_port: Optional[int] = None
    dest_port: Optional[int] = None
    interface: Optional[str] = None
    uid: Optional[int] = None
    comment: Optional[str] = None


@dataclass
class AppNetworkPolicy:
    """Network policy for an application."""

    app_name: str
    uid: int
    allowed: bool = True
    allowed_domains: Optional[Set[str]] = None
    allowed_ports: Optional[Set[int]] = None
    allowed_protocols: Optional[Set[Protocol]] = None
    blocked_domains: Optional[Set[str]] = None
    blocked_ports: Optional[Set[int]] = None


class FirewallControl:
    """iptables-based firewall control."""

    def __init__(self, use_ipv6: bool = True):
        """
        Initialize firewall control.

        Args:
            use_ipv6: Whether to manage IPv6 rules (ip6tables)
        """
        self.use_ipv6 = use_ipv6
        self.rules: Dict[str, FirewallRule] = {}
        self.app_policies: Dict[str, AppNetworkPolicy] = {}
        self._iptables_cmd = "iptables"
        self._ip6tables_cmd = "ip6tables" if use_ipv6 else None
        logger.info(f"Initialized FirewallControl (ipv6={use_ipv6})")

    def _run_iptables(
        self, args: List[str], ipv6: bool = False, check: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Run iptables command.

        Args:
            args: Command arguments
            ipv6: Use ip6tables instead of iptables
            check: Whether to raise on non-zero exit

        Returns:
            CompletedProcess instance

        Raises:
            NetworkError: If command fails
        """
        cmd = [self._ip6tables_cmd if ipv6 else self._iptables_cmd] + args

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check, timeout=10)
            return result
        except subprocess.CalledProcessError as e:
            raise NetworkError(
                f"iptables command failed: {' '.join(cmd)}",
                error_code="IPTABLES_FAILED",
                details={"stdout": e.stdout, "stderr": e.stderr, "returncode": e.returncode},
            )
        except subprocess.TimeoutExpired:
            raise NetworkError(
                f"iptables command timed out: {' '.join(cmd)}",
                error_code="IPTABLES_TIMEOUT",
            )
        except FileNotFoundError:
            raise NetworkError(
                f"iptables not found: {cmd[0]}",
                error_code="IPTABLES_NOT_FOUND",
                details={"cmd": cmd[0]},
            )

    def _build_rule_args(self, rule: FirewallRule) -> List[str]:
        """
        Build iptables arguments from FirewallRule.

        Args:
            rule: FirewallRule object

        Returns:
            List of iptables arguments
        """
        args = ["-A", rule.chain.value]

        if rule.protocol and rule.protocol != Protocol.ALL:
            args.extend(["-p", rule.protocol.value])

        if rule.source_ip:
            args.extend(["-s", rule.source_ip])

        if rule.dest_ip:
            args.extend(["-d", rule.dest_ip])

        if rule.source_port:
            args.extend(["--sport", str(rule.source_port)])

        if rule.dest_port:
            args.extend(["--dport", str(rule.dest_port)])

        if rule.interface:
            args.extend(["-i", rule.interface])

        if rule.uid is not None:
            args.extend(["-m", "owner", "--uid-owner", str(rule.uid)])

        if rule.comment:
            args.extend(["-m", "comment", "--comment", rule.comment])

        args.extend(["-j", rule.action.value])

        return args

    def add_rule(self, rule: FirewallRule, apply_ipv6: bool = False) -> bool:
        """
        Add a firewall rule.

        Args:
            rule: FirewallRule to add
            apply_ipv6: Also apply rule to IPv6

        Returns:
            True if successful, False otherwise

        Raises:
            NetworkError: If rule addition fails
        """
        args = self._build_rule_args(rule)

        try:
            # Add IPv4 rule
            self._run_iptables(args)
            logger.info(f"Added firewall rule: {rule.rule_id}")

            # Add IPv6 rule if requested
            if apply_ipv6 and self._ip6tables_cmd:
                self._run_iptables(args, ipv6=True)
                logger.info(f"Added IPv6 firewall rule: {rule.rule_id}")

            self.rules[rule.rule_id] = rule
            return True

        except NetworkError as e:
            logger.error(f"Failed to add firewall rule: {e}")
            raise

    def delete_rule(self, rule_id: str, apply_ipv6: bool = False) -> bool:
        """
        Delete a firewall rule.

        Args:
            rule_id: Rule ID to delete
            apply_ipv6: Also delete from IPv6

        Returns:
            True if successful, False if rule not found

        Raises:
            NetworkError: If rule deletion fails
        """
        if rule_id not in self.rules:
            logger.warning(f"Rule not found: {rule_id}")
            return False

        rule = self.rules[rule_id]
        args = self._build_rule_args(rule)
        # Change -A to -D for deletion
        args[0] = "-D"

        try:
            # Delete IPv4 rule
            self._run_iptables(args, check=False)
            logger.info(f"Deleted firewall rule: {rule_id}")

            # Delete IPv6 rule if requested
            if apply_ipv6 and self._ip6tables_cmd:
                self._run_iptables(args, ipv6=True, check=False)
                logger.info(f"Deleted IPv6 firewall rule: {rule_id}")

            del self.rules[rule_id]
            return True

        except NetworkError as e:
            logger.error(f"Failed to delete firewall rule: {e}")
            raise

    def list_rules(self, chain: Optional[Chain] = None) -> List[FirewallRule]:
        """
        List firewall rules.

        Args:
            chain: Filter by chain

        Returns:
            List of FirewallRule objects
        """
        rules = list(self.rules.values())
        if chain:
            rules = [r for r in rules if r.chain == chain]
        return rules

    def flush_rules(self, chain: Optional[Chain] = None) -> bool:
        """
        Flush firewall rules.

        Args:
            chain: Chain to flush, or None for all chains

        Returns:
            True if successful, False otherwise
        """
        try:
            if chain:
                self._run_iptables(["-F", chain.value])
                if self._ip6tables_cmd:
                    self._run_iptables(["-F", chain.value], ipv6=True)
                logger.info(f"Flushed chain: {chain.value}")
            else:
                self._run_iptables(["-F"])
                if self._ip6tables_cmd:
                    self._run_iptables(["-F"], ipv6=True)
                logger.info("Flushed all chains")

            # Clear tracked rules
            if chain:
                self.rules = {rid: r for rid, r in self.rules.items() if r.chain != chain}
            else:
                self.rules.clear()

            return True

        except NetworkError as e:
            logger.error(f"Failed to flush rules: {e}")
            return False

    def set_app_policy(self, policy: AppNetworkPolicy) -> bool:
        """
        Set network policy for an application.

        Args:
            policy: AppNetworkPolicy to apply

        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove existing policy rules for this app
            self._remove_app_rules(policy.app_name)

            if not policy.allowed:
                # Block all traffic for this UID
                rule = FirewallRule(
                    rule_id=f"{policy.app_name}_block_all",
                    chain=Chain.OUTPUT,
                    action=FirewallAction.DROP,
                    uid=policy.uid,
                    comment=f"Block {policy.app_name}",
                )
                self.add_rule(rule)
            else:
                # Allow traffic based on policy
                if policy.allowed_ports:
                    for port in policy.allowed_ports:
                        rule = FirewallRule(
                            rule_id=f"{policy.app_name}_allow_port_{port}",
                            chain=Chain.OUTPUT,
                            action=FirewallAction.ACCEPT,
                            dest_port=port,
                            uid=policy.uid,
                            comment=f"Allow {policy.app_name} port {port}",
                        )
                        self.add_rule(rule)

                # Block specific ports
                if policy.blocked_ports:
                    for port in policy.blocked_ports:
                        rule = FirewallRule(
                            rule_id=f"{policy.app_name}_block_port_{port}",
                            chain=Chain.OUTPUT,
                            action=FirewallAction.DROP,
                            dest_port=port,
                            uid=policy.uid,
                            comment=f"Block {policy.app_name} port {port}",
                        )
                        self.add_rule(rule)

            self.app_policies[policy.app_name] = policy
            logger.info(f"Applied network policy for: {policy.app_name}")
            return True

        except NetworkError as e:
            logger.error(f"Failed to set app policy: {e}")
            return False

    def _remove_app_rules(self, app_name: str) -> None:
        """
        Remove all rules for an application.

        Args:
            app_name: Application name
        """
        rule_ids = [rid for rid in self.rules.keys() if rid.startswith(f"{app_name}_")]
        for rule_id in rule_ids:
            try:
                self.delete_rule(rule_id)
            except NetworkError:
                pass

    def get_app_policy(self, app_name: str) -> Optional[AppNetworkPolicy]:
        """
        Get network policy for an application.

        Args:
            app_name: Application name

        Returns:
            AppNetworkPolicy or None if not found
        """
        return self.app_policies.get(app_name)

    def remove_app_policy(self, app_name: str) -> bool:
        """
        Remove network policy for an application.

        Args:
            app_name: Application name

        Returns:
            True if removed, False if not found
        """
        if app_name not in self.app_policies:
            logger.warning(f"App policy not found: {app_name}")
            return False

        self._remove_app_rules(app_name)
        del self.app_policies[app_name]
        logger.info(f"Removed network policy for: {app_name}")
        return True

    def block_app(self, app_name: str, uid: int) -> bool:
        """
        Block all network access for an application.

        Args:
            app_name: Application name
            uid: Application UID

        Returns:
            True if successful, False otherwise
        """
        policy = AppNetworkPolicy(app_name=app_name, uid=uid, allowed=False)
        return self.set_app_policy(policy)

    def allow_app(self, app_name: str, uid: int) -> bool:
        """
        Allow all network access for an application.

        Args:
            app_name: Application name
            uid: Application UID

        Returns:
            True if successful, False otherwise
        """
        policy = AppNetworkPolicy(app_name=app_name, uid=uid, allowed=True)
        return self.set_app_policy(policy)

    def set_default_policy(self, chain: Chain, action: FirewallAction) -> bool:
        """
        Set default policy for a chain.

        Args:
            chain: Chain to configure
            action: Default action (ACCEPT or DROP)

        Returns:
            True if successful, False otherwise
        """
        if action not in [FirewallAction.ACCEPT, FirewallAction.DROP]:
            raise NetworkError(
                f"Invalid default action: {action}",
                error_code="INVALID_ACTION",
                details={"action": action.value},
            )

        try:
            self._run_iptables(["-P", chain.value, action.value])
            if self._ip6tables_cmd:
                self._run_iptables(["-P", chain.value, action.value], ipv6=True)
            logger.info(f"Set default policy for {chain.value}: {action.value}")
            return True

        except NetworkError as e:
            logger.error(f"Failed to set default policy: {e}")
            return False

    def save_rules(self, output_file: str) -> bool:
        """
        Save current rules to file.

        Args:
            output_file: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["iptables-save"], capture_output=True, text=True, check=True, timeout=5
            )
            with open(output_file, "w") as f:
                f.write(result.stdout)
            logger.info(f"Saved firewall rules to: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save rules: {e}")
            return False

    def restore_rules(self, input_file: str) -> bool:
        """
        Restore rules from file.

        Args:
            input_file: Input file path

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(input_file, "r") as f:
                subprocess.run(
                    ["iptables-restore"], stdin=f, check=True, capture_output=True, timeout=10
                )
            logger.info(f"Restored firewall rules from: {input_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to restore rules: {e}")
            return False
