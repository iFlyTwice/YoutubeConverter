from typing import Dict, List, Callable
import logging

logger = logging.getLogger(__name__)

class EventManager:
    """
    Manages event subscriptions and notifications between components
    """
    _instance = None
    _subscribers: Dict[str, List[Callable]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def subscribe(cls, event_name: str, callback: Callable) -> None:
        """Subscribe to an event"""
        if event_name not in cls._subscribers:
            cls._subscribers[event_name] = []
        if callback not in cls._subscribers[event_name]:
            cls._subscribers[event_name].append(callback)
            logger.debug(f"Subscribed to event: {event_name}")

    @classmethod
    def unsubscribe(cls, event_name: str, callback: Callable) -> None:
        """Unsubscribe from an event"""
        if event_name in cls._subscribers and callback in cls._subscribers[event_name]:
            cls._subscribers[event_name].remove(callback)
            logger.debug(f"Unsubscribed from event: {event_name}")

    @classmethod
    def notify(cls, event_name: str, *args, **kwargs) -> None:
        """Notify all subscribers of an event"""
        if event_name in cls._subscribers:
            for callback in cls._subscribers[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in event callback for {event_name}: {str(e)}")
                    
    @classmethod
    def emit(cls, event_name: str, *args, **kwargs) -> None:
        """Alias for notify method"""
        cls.notify(event_name, *args, **kwargs)
