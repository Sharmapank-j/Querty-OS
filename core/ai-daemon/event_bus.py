"""
Event Bus for Inter-Service Communication

Simple publish-subscribe event bus for decoupled communication between services.
"""

import logging
import threading
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class Event:
    """Represents an event in the system."""

    def __init__(self, event_type: str, data: Any = None, source: Optional[str] = None):
        """
        Initialize an event.

        Args:
            event_type: Type/name of the event
            data: Event payload data
            source: Source service/component that generated the event
        """
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary.

        Returns:
            Dictionary representation of the event
        """
        return {
            "event_type": self.event_type,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
        }


class EventBus:
    """
    Simple publish-subscribe event bus for inter-service communication.

    Allows services to publish events and subscribe to event types without tight coupling.
    """

    def __init__(self):
        """Initialize the event bus."""
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.lock = threading.RLock()
        self.event_history: List[Event] = []
        self.max_history_size = 1000
        logger.info("Event bus initialized")

    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to (use "*" for all events)
            callback: Function to call when event is published
        """
        with self.lock:
            if callback not in self.subscribers[event_type]:
                self.subscribers[event_type].append(callback)
                logger.debug(f"Subscribed to event type: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
        """
        with self.lock:
            if event_type in self.subscribers and callback in self.subscribers[event_type]:
                self.subscribers[event_type].remove(callback)
                logger.debug(f"Unsubscribed from event type: {event_type}")

    def publish(self, event_type: str, data: Any = None, source: Optional[str] = None) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event_type: Type of event
            data: Event payload data
            source: Source service/component
        """
        event = Event(event_type, data, source)

        # Store in history
        with self.lock:
            self.event_history.append(event)
            if len(self.event_history) > self.max_history_size:
                self.event_history.pop(0)

        logger.debug(f"Publishing event: {event_type} from {source}")

        # Notify specific subscribers
        self._notify_subscribers(event_type, event)

        # Notify wildcard subscribers
        self._notify_subscribers("*", event)

    def _notify_subscribers(self, event_type: str, event: Event) -> None:
        """
        Notify subscribers of an event type.

        Args:
            event_type: Type of event
            event: Event object
        """
        with self.lock:
            callbacks = self.subscribers.get(event_type, []).copy()

        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(
                    f"Error in event callback for {event_type}: {e}",
                    exc_info=True,
                )

    def publish_async(
        self, event_type: str, data: Any = None, source: Optional[str] = None
    ) -> None:
        """
        Publish an event asynchronously (non-blocking).

        Args:
            event_type: Type of event
            data: Event payload data
            source: Source service/component
        """
        thread = threading.Thread(
            target=self.publish,
            args=(event_type, data, source),
            daemon=True,
        )
        thread.start()

    def get_history(
        self,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100,
    ) -> List[Event]:
        """
        Get event history with optional filtering.

        Args:
            event_type: Filter by event type (None for all)
            source: Filter by source (None for all)
            limit: Maximum number of events to return

        Returns:
            List of events matching the criteria
        """
        with self.lock:
            events = self.event_history.copy()

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if source:
            events = [e for e in events if e.source == source]

        return events[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        with self.lock:
            self.event_history.clear()
        logger.info("Event history cleared")

    def get_subscribers_count(self, event_type: Optional[str] = None) -> int:
        """
        Get count of subscribers.

        Args:
            event_type: Specific event type, or None for total count

        Returns:
            Number of subscribers
        """
        with self.lock:
            if event_type:
                return len(self.subscribers.get(event_type, []))
            else:
                return sum(len(subs) for subs in self.subscribers.values())

    def get_all_event_types(self) -> List[str]:
        """
        Get all event types that have subscribers.

        Returns:
            List of event types
        """
        with self.lock:
            return list(self.subscribers.keys())
