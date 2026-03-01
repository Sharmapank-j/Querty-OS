"""
State Manager for System State Persistence

Manages system state persistence using JSON file storage with atomic writes.
"""

import json
import logging
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class StateManager:
    """
    System state persistence manager using JSON file storage.

    Provides thread-safe state management with atomic writes and backup functionality.
    """

    def __init__(self, state_file: str = "/var/lib/querty-os/state.json"):
        """
        Initialize the state manager.

        Args:
            state_file: Path to the state file
        """
        self.state_file = Path(state_file)
        self.backup_file = Path(str(state_file) + ".backup")
        self.lock = threading.RLock()
        self.state: Dict[str, Any] = {}
        self.last_save_time: Optional[datetime] = None

        # Ensure directory exists
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            logger.warning(
                f"Cannot create state directory {self.state_file.parent}: {e}, "
                f"using fallback location"
            )
            # Fallback to user's home directory or /tmp
            fallback_dir = Path.home() / ".querty-os"
            try:
                fallback_dir.mkdir(parents=True, exist_ok=True)
                self.state_file = fallback_dir / "state.json"
                self.backup_file = fallback_dir / "state.json.backup"
            except Exception as e2:
                logger.warning(f"Cannot create fallback directory: {e2}, using /tmp")
                self.state_file = Path("/tmp/querty-os-state.json")
                self.backup_file = Path("/tmp/querty-os-state.json.backup")

        # Load existing state
        self.load()

        logger.info(f"State manager initialized with file: {self.state_file}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the state.

        Args:
            key: State key (supports dot notation for nested keys)
            default: Default value if key not found

        Returns:
            Value from state or default
        """
        with self.lock:
            keys = key.split(".")
            value = self.state

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default

            return value

    def set(self, key: str, value: Any, persist: bool = True) -> None:
        """
        Set a value in the state.

        Args:
            key: State key (supports dot notation for nested keys)
            value: Value to set
            persist: Whether to immediately persist to disk
        """
        with self.lock:
            keys = key.split(".")
            state = self.state

            # Navigate to the parent dictionary
            for k in keys[:-1]:
                if k not in state:
                    state[k] = {}
                state = state[k]

            # Set the value
            state[keys[-1]] = value

            if persist:
                self.save()

    def delete(self, key: str, persist: bool = True) -> bool:
        """
        Delete a key from the state.

        Args:
            key: State key to delete
            persist: Whether to immediately persist to disk

        Returns:
            True if key was deleted, False if not found
        """
        with self.lock:
            keys = key.split(".")
            state = self.state

            # Navigate to the parent dictionary
            for k in keys[:-1]:
                if k not in state:
                    return False
                state = state[k]

            # Delete the key
            if keys[-1] in state:
                del state[keys[-1]]
                if persist:
                    self.save()
                return True

            return False

    def update(self, updates: Dict[str, Any], persist: bool = True) -> None:
        """
        Update multiple values in the state.

        Args:
            updates: Dictionary of key-value pairs to update
            persist: Whether to immediately persist to disk
        """
        with self.lock:
            for key, value in updates.items():
                self.set(key, value, persist=False)

            if persist:
                self.save()

    def get_all(self) -> Dict[str, Any]:
        """
        Get the entire state.

        Returns:
            Complete state dictionary
        """
        with self.lock:
            return self.state.copy()

    def clear(self, persist: bool = True) -> None:
        """
        Clear all state.

        Args:
            persist: Whether to immediately persist to disk
        """
        with self.lock:
            self.state = {}
            if persist:
                self.save()

    def save(self) -> bool:
        """
        Save state to disk atomically.

        Returns:
            True if save succeeded, False otherwise
        """
        with self.lock:
            try:
                # Write to temporary file first
                temp_file = Path(str(self.state_file) + ".tmp")
                with open(temp_file, "w") as f:
                    json.dump(
                        {
                            "state": self.state,
                            "timestamp": datetime.now().isoformat(),
                        },
                        f,
                        indent=2,
                    )

                # Backup existing file if it exists
                if self.state_file.exists():
                    shutil.copy2(self.state_file, self.backup_file)

                # Atomic rename
                temp_file.replace(self.state_file)

                self.last_save_time = datetime.now()
                logger.debug(f"State saved to {self.state_file}")
                return True

            except Exception as e:
                logger.error(f"Failed to save state: {e}", exc_info=True)
                return False

    def load(self) -> bool:
        """
        Load state from disk.

        Returns:
            True if load succeeded, False otherwise
        """
        with self.lock:
            try:
                if self.state_file.exists():
                    with open(self.state_file, "r") as f:
                        data = json.load(f)
                        self.state = data.get("state", {})
                    logger.info(f"State loaded from {self.state_file}")
                    return True
                else:
                    logger.info("No existing state file found, starting with empty state")
                    return True

            except Exception as e:
                logger.error(f"Failed to load state: {e}", exc_info=True)

                # Try to load from backup
                if self.backup_file.exists():
                    try:
                        with open(self.backup_file, "r") as f:
                            data = json.load(f)
                            self.state = data.get("state", {})
                        logger.warning("State loaded from backup file")
                        return True
                    except Exception as e2:
                        logger.error(f"Failed to load backup state: {e2}", exc_info=True)

                return False

    def restore_backup(self) -> bool:
        """
        Restore state from backup file.

        Returns:
            True if restore succeeded, False otherwise
        """
        with self.lock:
            if not self.backup_file.exists():
                logger.error("No backup file found")
                return False

            try:
                shutil.copy2(self.backup_file, self.state_file)
                return self.load()
            except Exception as e:
                logger.error(f"Failed to restore backup: {e}", exc_info=True)
                return False

    def export_to_file(self, export_path: str) -> bool:
        """
        Export state to a file.

        Args:
            export_path: Path to export file

        Returns:
            True if export succeeded, False otherwise
        """
        with self.lock:
            try:
                with open(export_path, "w") as f:
                    json.dump(
                        {
                            "state": self.state,
                            "timestamp": datetime.now().isoformat(),
                            "source": str(self.state_file),
                        },
                        f,
                        indent=2,
                    )
                logger.info(f"State exported to {export_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to export state: {e}", exc_info=True)
                return False

    def import_from_file(self, import_path: str, persist: bool = True) -> bool:
        """
        Import state from a file.

        Args:
            import_path: Path to import file
            persist: Whether to immediately persist to disk

        Returns:
            True if import succeeded, False otherwise
        """
        with self.lock:
            try:
                with open(import_path, "r") as f:
                    data = json.load(f)
                    self.state = data.get("state", {})

                if persist:
                    self.save()

                logger.info(f"State imported from {import_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to import state: {e}", exc_info=True)
                return False
