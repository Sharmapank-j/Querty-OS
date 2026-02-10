#!/usr/bin/env python3
"""
Querty-OS Memory Manager
Manages LLM context windows, task history, and memory purging.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("querty-memory-manager")


@dataclass
class TaskMemory:
    """Stores task history and metadata."""

    task_id: str
    task_type: str
    timestamp: datetime
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    token_count: int = 0
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert task memory to dictionary."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "timestamp": self.timestamp.isoformat(),
            "input_data": self.input_data,
            "output_data": self.output_data,
            "token_count": self.token_count,
            "priority": self.priority,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskMemory":
        """Create TaskMemory from dictionary."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    def get_size(self) -> int:
        """Estimate memory size in bytes."""
        return len(json.dumps(self.to_dict()).encode("utf-8"))


@dataclass
class PurgeRules:
    """Memory cleanup policies."""

    max_context_tokens: int = 8192
    max_task_history: int = 100
    min_priority_threshold: int = 1
    max_age_days: int = 7
    preserve_critical: bool = True

    def should_purge(self, task: TaskMemory) -> bool:
        """
        Determine if a task should be purged.

        Args:
            task: Task memory to evaluate

        Returns:
            True if task should be purged
        """
        if self.preserve_critical and task.priority >= 5:
            return False

        age = datetime.now() - task.timestamp
        if age > timedelta(days=self.max_age_days):
            return True

        if task.priority < self.min_priority_threshold:
            return True

        return False


class ContextWindowManager:
    """Manages LLM context window and memory optimization."""

    def __init__(
        self,
        max_tokens: int = 8192,
        storage_path: Optional[Path] = None,
        purge_rules: Optional[PurgeRules] = None,
    ):
        """
        Initialize context window manager.

        Args:
            max_tokens: Maximum context window size in tokens
            storage_path: Path for persistent storage
            purge_rules: Memory purging rules
        """
        self.max_tokens = max_tokens
        self.storage_path = storage_path or Path.home() / ".querty" / "memory"
        self.purge_rules = purge_rules or PurgeRules(max_context_tokens=max_tokens)
        self.task_history: List[TaskMemory] = []
        self.current_tokens = 0
        self._initialize_storage()
        logger.info(f"ContextWindowManager initialized with max_tokens={max_tokens}")

    def _initialize_storage(self):
        """Initialize persistent storage directory."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._load_history()

    def _load_history(self):
        """Load task history from persistent storage."""
        history_file = self.storage_path / "task_history.json"
        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    data = json.load(f)
                    self.task_history = [TaskMemory.from_dict(t) for t in data]
                    self.current_tokens = sum(t.token_count for t in self.task_history)
                    logger.info(f"Loaded {len(self.task_history)} tasks from history")
            except Exception as e:
                logger.error(f"Error loading task history: {e}")
                self.task_history = []

    def save_history(self):
        """Save task history to persistent storage."""
        history_file = self.storage_path / "task_history.json"
        try:
            with open(history_file, "w") as f:
                json.dump([t.to_dict() for t in self.task_history], f, indent=2)
            logger.debug("Task history saved")
        except Exception as e:
            logger.error(f"Error saving task history: {e}")

    def add_task(self, task: TaskMemory):
        """
        Add a task to memory.

        Args:
            task: Task memory to add
        """
        self.task_history.append(task)
        self.current_tokens += task.token_count
        logger.debug(
            f"Added task {task.task_id}, current_tokens={self.current_tokens}/{self.max_tokens}"
        )

        if self.current_tokens > self.max_tokens:
            self.purge_memory()

        if len(self.task_history) > self.purge_rules.max_task_history:
            self.purge_memory()

    def purge_memory(self):
        """Clean up memory based on purge rules."""
        logger.info("Starting memory purge")
        initial_count = len(self.task_history)
        initial_tokens = self.current_tokens

        tasks_to_keep = [t for t in self.task_history if not self.purge_rules.should_purge(t)]

        if len(tasks_to_keep) == len(self.task_history):
            tasks_to_keep.sort(key=lambda t: (t.priority, t.timestamp))
            target_count = self.purge_rules.max_task_history // 2
            tasks_to_keep = tasks_to_keep[-target_count:]

        self.task_history = tasks_to_keep
        self.current_tokens = sum(t.token_count for t in self.task_history)

        purged_count = initial_count - len(self.task_history)
        purged_tokens = initial_tokens - self.current_tokens

        logger.info(
            f"Purged {purged_count} tasks, freed {purged_tokens} tokens. "
            f"Current: {len(self.task_history)} tasks, {self.current_tokens} tokens"
        )

        self.save_history()

    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get summary of current context state.

        Returns:
            Context statistics
        """
        return {
            "total_tasks": len(self.task_history),
            "current_tokens": self.current_tokens,
            "max_tokens": self.max_tokens,
            "utilization": self.current_tokens / self.max_tokens if self.max_tokens > 0 else 0,
            "oldest_task": (
                self.task_history[0].timestamp.isoformat() if self.task_history else None
            ),
            "newest_task": (
                self.task_history[-1].timestamp.isoformat() if self.task_history else None
            ),
        }

    def get_recent_tasks(self, count: int = 10) -> List[TaskMemory]:
        """
        Get most recent tasks.

        Args:
            count: Number of tasks to retrieve

        Returns:
            List of recent task memories
        """
        return self.task_history[-count:]

    def clear_all(self):
        """Clear all task history."""
        logger.warning("Clearing all task history")
        self.task_history = []
        self.current_tokens = 0
        self.save_history()

    def optimize_context(self) -> int:
        """
        Optimize context by removing redundant information.

        Returns:
            Number of tokens freed
        """
        initial_tokens = self.current_tokens
        logger.info("Optimizing context window")

        task_groups: Dict[str, List[TaskMemory]] = {}
        for task in self.task_history:
            task_groups.setdefault(task.task_type, []).append(task)

        optimized_tasks = []
        for task_type, tasks in task_groups.items():
            if len(tasks) > 5:
                tasks.sort(key=lambda t: (t.priority, t.timestamp), reverse=True)
                optimized_tasks.extend(tasks[:3])
            else:
                optimized_tasks.extend(tasks)

        self.task_history = sorted(optimized_tasks, key=lambda t: t.timestamp)
        self.current_tokens = sum(t.token_count for t in self.task_history)

        freed_tokens = initial_tokens - self.current_tokens
        logger.info(f"Context optimization freed {freed_tokens} tokens")
        self.save_history()

        return freed_tokens
