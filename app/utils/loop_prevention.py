import time
from functools import wraps
from flask import request, abort
from threading import Thread
import threading
import logging

logger = logging.getLogger(__name__)

class LoopPreventionMiddleware:
    def __init__(self, app, timeout=30):
        self.app = app
        self.timeout = timeout
        self.request_times = {}
        self.lock = threading.Lock()
        self._setup_logging()

    def __call__(self, environ, start_response):
        thread = Thread(target=self._handle_request, args=(environ, start_response))
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.timeout)
        
        if thread.is_alive():
            logger.warning(f"Request timeout detected for {environ.get('PATH_INFO')}")
            abort(503, description="Request timed out - possible infinite loop detected")
        
        return self.response

    def _handle_request(self, environ, start_response):
        request_id = environ.get('HTTP_X_REQUEST_ID', str(time.time()))
        path = environ.get('PATH_INFO', '')
        
        with self.lock:
            if request_id in self.request_times:
                if time.time() - self.request_times[request_id] < 0.1:
                    logger.warning(f"Rapid requests detected for {path}")
                    abort(429, description="Too many rapid requests - possible infinite loop")
            self.request_times[request_id] = time.time()

        try:
            self.response = self.app(environ, start_response)
        except Exception as e:
            logger.error(f"Error in request {request_id}: {str(e)}")
            raise
        finally:
            with self.lock:
                self.request_times.pop(request_id, None)

    def _setup_logging(self):
        """Setup logging configuration"""
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

def prevent_infinite_loops(func):
    """Decorator to prevent infinite loops in recursive functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        call_count = getattr(wrapper, 'call_count', 0)
        wrapper.call_count = call_count + 1
        
        if call_count > 1000:  # Adjust threshold as needed
            logger.error(f"Maximum recursion depth exceeded in {func.__name__}")
            raise RuntimeError("Maximum recursion depth exceeded - possible infinite loop")
        
        try:
            result = func(*args, **kwargs)
            wrapper.call_count -= 1
            return result
        except Exception as e:
            wrapper.call_count -= 1
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper