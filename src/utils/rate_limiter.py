import time
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    """Rate limiter per API calls"""
    
    def __init__(self, max_calls: int, period_seconds: int):
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls = deque()
    
    def can_proceed(self) -> bool:
        """Controlla se possiamo fare altra call"""
        now = time.time()
        
        # Rimuovi calls vecchie
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        
        return len(self.calls) < self.max_calls
    
    def wait_if_needed(self):
        """Aspetta se necessario per rispettare rate limit"""
        while not self.can_proceed():
            time.sleep(1)
        
        self.calls.append(time.time())
