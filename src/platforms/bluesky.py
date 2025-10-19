from atproto import Client
from typing import Optional, Dict
import io

class BlueskyPublisher:
    """Manages Bluesky publishing with image support"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.client = None
        self.logged_in = False
    
    def login(self):
        """Login to Bluesky"""
        try:
            print(f"🔐 Logging into Bluesky as {self.username}...")
            
            self.client = Client()
            self.client.login(self.username, self.password)
            self.logged_in = True
            
            # Get profile info
            profile = self.client.app.bsky.actor.get_profile(
                {"actor": self.username}
            )
            
            print(f"✅ Login successful!")
            print(f"   👤 Handle: @{profile.handle}")
            print(f"   👥 Followers: {profile.followers_count}")
            print(f"   📝 Posts: {profile.posts_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Bluesky login error: {e}")
            print(f"   Check username and password in .env")
            self.logged_in = False
            return False
    
    def upload_image(self, image_bytes: bytes) -> Optional[Dict]:
        """
        Upload image to Bluesky
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Upload result with blob reference
        """
        try:
            print(f"📸 Uploading image to Bluesky...")
            
            # Upload blob
            upload = self.client.com.atproto.repo.upload_blob(image_bytes)
            
            print(f"✅ Image uploaded successfully!")
            return {
                'blob': upload.blob,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Image upload error: {e}")
            return None
    
    def post(self, content: str, image_bytes: Optional[bytes] = None) -> Optional[Dict]:
        """
        Publish post on Bluesky with optional image
        
        Args:
            content: Post text (max 300 characters)
            image_bytes: Optional image data
        
        Returns:
            Dict with post info, or None if error
        """
        if not self.logged_in:
            if not self.login():
                return None
        
        # Check length
        if len(content) > 300:
            print(f"⚠️ Post too long ({len(content)}), truncating to 300")
            content = content[:297] + "..."
        
        try:
            print(f"📤 Publishing post on Bluesky...")
            
            # Prepare post data
            post_data = {
                'text': content
            }
            
            # Add image if provided
            if image_bytes:
                upload_result = self.upload_image(image_bytes)
                if upload_result:
                    post_data['embed'] = {
                        '$type': 'app.bsky.embed.images',
                        'images': [{
                            'alt': 'AI-generated image for tech post',
                            'image': upload_result['blob']
                        }]
                    }
                    print(f"🖼️  Image attached to post")
            
            # Publish post
            response = self.client.send_post(**post_data)
            
            # Build post URL
            post_id = response.uri.split('/')[-1]
            post_url = f"https://bsky.app/profile/{self.username}/post/{post_id}"
            
            result = {
                'success': True,
                'uri': response.uri,
                'cid': response.cid,
                'url': post_url,
                'has_image': image_bytes is not None
            }
            
            print(f"✅ Post published!")
            print(f"   🔗 URL: {post_url}")
            
            return result
            
        except Exception as e:
            print(f"❌ Publication error DETAILED:")
            print(f"   Type: {type(e).__name__}")
            print(f"   Message: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
