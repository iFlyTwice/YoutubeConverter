import threading
import queue
import logging
from typing import Optional, Callable, Tuple, Any

logger = logging.getLogger(__name__)

class SettingsPageThread(threading.Thread):
    """Thread class for handling background operations in settings page"""
    
    def __init__(self):
        super().__init__()
        self.task_queue = queue.Queue()
        self.callbacks = {}
        self.daemon = True
        self._stop_event = threading.Event()
        
    def run(self):
        """Process tasks from the queue"""
        while not self._stop_event.is_set():
            try:
                task_name, args = self.task_queue.get(timeout=1.0)
                if task_name in self.callbacks:
                    try:
                        result = self.callbacks[task_name](args) if args is not None else self.callbacks[task_name]()
                        logger.debug(f"Task {task_name} completed successfully")
                    except Exception as e:
                        logger.error(f"Error executing task {task_name}: {str(e)}")
                        result = None
                self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in settings page thread: {str(e)}")
                
    def add_task(self, task: Tuple[str, Any]):
        """Add a task to the queue"""
        self.task_queue.put(task)
        
    def register_callback(self, task_name: str, callback: Callable):
        """Register a callback for a specific task"""
        self.callbacks[task_name] = callback
        
    def stop(self):
        """Signal the thread to stop"""
        self._stop_event.set()
        
    def stopped(self):
        """Check if the thread has been stopped"""
        return self._stop_event.is_set()
