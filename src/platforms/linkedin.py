"""
LinkedIn Publisher - Professional network posting
"""

import requests
from typing import Optional, Dict
from .base_publisher import BasePublisher
import base64

class LinkedInPublisher(BasePublisher):
    """Manages LinkedIn publishing"""
    
    def __init__(self, access_token: str, user_id: str):
        self.access_token = access_token
        self.user_id = user_id
        self.logged_in = False
        self.base_url = "https://api.linkedin.com/v2"
    
    @property
    def platform_name(self) -> str:
        return "linkedin"
    
    @property
    def max_length(self) -> int:
        return 3000  # LinkedIn allows longer posts
    
    def login(self) -> bool:
        """Verify LinkedIn credentials"""
        try:
            print(f"🔐 Verifying LinkedIn credentials...")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ LinkedIn verified!")
                self.logged_in = True
                return True
            else:
                print(f"❌ LinkedIn verification failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ LinkedIn error: {e}")
            return False
    
    def upload_image(self, image_bytes: bytes) -> Optional[str]:
        """Upload image to LinkedIn"""
        try:
            print(f"📸 Uploading image to LinkedIn...")
            
            # Register upload
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:person:{self.user_id}",
                    "serviceRelationships": [{
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }]
                }
            }
            
            response = requests.post(
                f"{self.base_url}/assets?action=registerUpload",
                headers=headers,
                json=register_data,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ Image registration failed")
                return None
            
            data = response.json()
            upload_url = data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset = data['value']['asset']
            
            # Upload image
            upload_headers = {
                'Authorization': f'Bearer {self.access_token}',
            }
            
            upload_response = requests.put(
                upload_url,
                headers=upload_headers,
                data=image_bytes,
                timeout=60
            )
            
            if upload_response.status_code in [200, 201]:
                print(f"✅ Image uploaded to LinkedIn!")
                return asset
            else:
                print(f"❌ Image upload failed")
                return None
                
        except Exception as e:
            print(f"❌ LinkedIn image upload error: {e}")
            return None
    
    def post(self, content: str, image_bytes: Optional[bytes] = None) -> Optional[Dict]:
        """Publish post on LinkedIn"""
        if not self.logged_in:
            if not self.login():
                return None
        
        if len(content) > self.max_length:
            content = content[:self.max_length - 3] + "..."
        
        try:
            print(f"📤 Publishing to LinkedIn...")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            post_data = {
                "author": f"urn:li:person:{self.user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Add image if provided
            if image_bytes:
                asset = self.upload_image(image_bytes)
                if asset:
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                        "status": "READY",
                        "description": {
                            "text": "AI-generated tech visualization"
                        },
                        "media": asset,
                        "title": {
                            "text": "Tech Post"
                        }
                    }]
            
            response = requests.post(
                f"{self.base_url}/ugcPosts",
                headers=headers,
                json=post_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                post_id = response.headers.get('X-RestLi-Id', 'unknown')
                
                result = {
                    'success': True,
                    'post_id': post_id,
                    'url': f"https://www.linkedin.com/feed/update/{post_id}",
                    'has_image': image_bytes is not None,
                    'platform': self.platform_name
                }
                
                print(f"✅ Posted to LinkedIn!")
                print(f"   🔗 {result['url']}")
                
                return result
            else:
                print(f"❌ LinkedIn post failed: {response.status_code}")
                print(f"   {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ LinkedIn error: {e}")
            return None
