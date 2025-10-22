"""
Mastodon Publisher - Federated social network
"""

from mastodon import Mastodon
from typing import Optional, Dict
from .base_publisher import BasePublisher

class MastodonPublisher(BasePublisher):
    """Manages Mastodon publishing"""
    
    def __init__(self, instance_url: str, access_token: str):
        self.instance_url = instance_url
        self.access_token = access_token
        self.client = None
        self.logged_in = False
    
    @property
    def platform_name(self) -> str:
        return "mastodon"
    
    @property
    def max_length(self) -> int:
        return 500  # Default Mastodon limit
    
    def login(self) -> bool:
        """Connect to Mastodon instance"""
        try:
            print(f"🔐 Connecting to Mastodon ({self.instance_url})...")
            
            self.client = Mastodon(
                access_token=self.access_token,
                api_base_url=self.instance_url
            )
            
            # Verify credentials
            account = self.client.account_verify_credentials()
            
            print(f"✅ Mastodon connected!")
            print(f"   👤 @{account['username']}")
            print(f"   👥 Followers: {account['followers_count']}")
            
            self.logged_in = True
            return True
            
        except Exception as e:
            print(f"❌ Mastodon error: {e}")
            return False
    
    def post(self, content: str, image_bytes: Optional[bytes] = None) -> Optional[Dict]:
        """Publish post on Mastodon"""
        if not self.logged_in:
            if not self.login():
                return None
        
        if len(content) > self.max_length:
            content = content[:self.max_length - 3] + "..."
        
        try:
            print(f"📤 Publishing to Mastodon...")
            
            media_ids = None
            if image_bytes:
                print(f"📸 Uploading image...")
                media = self.client.media_post(
                    image_bytes,
                    mime_type='image/jpeg',
                    description='AI-generated tech visualization'
                )
                media_ids = [media['id']]
                print(f"🖼️  Image uploaded")
            
            status = self.client.status_post(
                content,
                media_ids=media_ids,
                visibility='public'
            )
            
            result = {
                'success': True,
                'post_id': status['id'],
                'url': status['url'],
                'has_image': image_bytes is not None,
                'platform': self.platform_name
            }
            
            print(f"✅ Posted to Mastodon!")
            print(f"   🔗 {result['url']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Mastodon error: {e}")
            return None
