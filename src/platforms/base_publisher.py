"""
Base Publisher - Interface for all social platforms
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict

class BasePublisher(ABC):
    """Abstract base class for social media publishers"""
    
    @abstractmethod
    def login(self) -> bool:
        """Login to platform"""
        pass
    
    @abstractmethod
    def post(self, content: str, image_bytes: Optional[bytes] = None) -> Optional[Dict]:
        """
        Publish content to platform
        
        Args:
            content: Post text
            image_bytes: Optional image
            
        Returns:
            Dict with post info or None if failed
        """
        pass
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Platform identifier"""
        pass
    
    @property
    @abstractmethod
    def max_length(self) -> int:
        """Maximum post length for this platform"""
        pass
