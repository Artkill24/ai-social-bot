from atproto import Client
from typing import Optional, Dict
from .base_publisher import BasePublisher

class BlueskyPublisher(BasePublisher):
    """Manages Bluesky publishing with image support"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.client = None
        self.logged_in = False
    
    @property
    def platform_name(self) -> str:
        return "bluesky"
    
    @property
    def max_length(self) -> int:
        return 300
    
    def login(self) -> bool:
        """Login to Bluesky"""
        try:
            print(f"🔐 Logging into Bluesky as {self.username}...")
            
            self.client = Client()
            self.client.login(self.username, self.password)
            self.logged_in = True
            
            profile = self.client.app.bsky.actor.get_profile(
                {"actor": self.username}
            )
            
            print(f"✅ Bluesky login successful!")
            print(f"   👤 Handle: @{profile.handle}")
            print(f"   👥 Followers: {profile.followers_count}")
            print(f"   📝 Posts: {profile.posts_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Bluesky login error: {e}")
            self.logged_in = False
            return False
    
    def upload_image(self, image_bytes: bytes) -> Optional[Dict]:
        """Upload image to Bluesky"""
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"   🔄 Retry {attempt + 1}/{max_retries}...")
                
                print(f"📸 Uploading image ({len(image_bytes) / 1024:.1f}KB)...")
                upload = self.client.com.atproto.repo.upload_blob(image_bytes)
                
                print(f"✅ Image uploaded successfully!")
                return {'blob': upload.blob, 'success': True}
                
            except Exception as e:
                print(f"⚠️ Upload attempt {attempt + 1} failed: {type(e).__name__}")
                if attempt == max_retries - 1:
                    print(f"❌ Image upload failed after {max_retries} attempts")
                    return None
        
        return None
    
    def post(self, content: str, image_bytes: Optional[bytes] = None) -> Optional[Dict]:
        """Publish post on Bluesky"""
        if not self.logged_in:
            if not self.login():
                return None
        
        if len(content) > self.max_length:
            print(f"⚠️ Post too long ({len(content)}), truncating")
            content = content[:self.max_length - 3] + "..."
        
        try:
            print(f"📤 Publishing to Bluesky...")
            
            post_data = {'text': content}
            has_image = False
            
            if image_bytes:
                upload_result = self.upload_image(image_bytes)
                if upload_result:
                    post_data['embed'] = {
                        '$type': 'app.bsky.embed.images',
                        'images': [{
                            'alt': 'AI-generated tech visualization',
                            'image': upload_result['blob']
                        }]
                    }
                    has_image = True
                    print(f"🖼️  Image attached")
                else:
                    print(f"⚠️ Posting without image")
            
            response = self.client.send_post(**post_data)
            post_id = response.uri.split('/')[-1]
            post_url = f"https://bsky.app/profile/{self.username}/post/{post_id}"
            
            result = {
                'success': True,
                'uri': response.uri,
                'cid': response.cid,
                'url': post_url,
                'has_image': has_image,
                'platform': self.platform_name
            }
            
            print(f"✅ Posted to Bluesky!")
            print(f"   🔗 {post_url}")
            
            return result
            
        except Exception as e:
            print(f"❌ Bluesky error: {type(e).__name__}: {str(e)}")
            return None
