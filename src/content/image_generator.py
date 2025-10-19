"""
Image Generator using Cloudflare Workers AI
Generates images for social media posts using AI
"""

import requests
import os
from typing import Optional, Dict
import time

class ImageGenerator:
    """Generates images using Cloudflare Workers AI (FREE!)"""
    
    def __init__(self, account_id: str, api_token: str):
        self.account_id = account_id
        self.api_token = api_token
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/"
        
        # Available models
        self.models = {
            'stable-diffusion': '@cf/stabilityai/stable-diffusion-xl-base-1.0',
            'fast': '@cf/bytedance/stable-diffusion-xl-lightning'
        }
    
    def generate_image_prompt(self, topic: str) -> str:
        """
        Generate an appropriate image prompt from post topic
        
        Args:
            topic: The post topic
            
        Returns:
            Optimized prompt for image generation
        """
        # Clean and optimize the topic for image generation
        prompts = {
            'ai': "modern AI neural network visualization, abstract blue and purple gradients, tech aesthetic, minimalist, professional",
            'coding': "developer workspace with code on screen, modern minimalist setup, blue and green tones, professional photography",
            'javascript': "JavaScript code visualization, colorful syntax highlighting, modern tech aesthetic",
            'python': "Python programming visualization, clean code editor, blue and yellow tones",
            'cloud': "cloud computing infrastructure visualization, modern tech aesthetic, blue tones",
            'security': "cybersecurity shield visualization, digital protection, blue and green secure aesthetic",
            'database': "database architecture visualization, connected nodes, modern tech design",
            'api': "API connection visualization, data flow diagram, modern minimalist style",
            'docker': "container orchestration visualization, modern DevOps aesthetic, blue tones",
            'github': "Git workflow visualization, version control diagram, developer aesthetic",
            'default': "modern technology abstract visualization, professional aesthetic, blue and purple gradients"
        }
        
        # Try to match topic keywords
        topic_lower = topic.lower()
        for key, prompt in prompts.items():
            if key in topic_lower:
                return prompt
        
        return prompts['default']
    
    def generate(self, prompt: str, model: str = 'fast') -> Optional[bytes]:
        """
        Generate image using Cloudflare Workers AI
        
        Args:
            prompt: Image generation prompt
            model: Model to use ('stable-diffusion' or 'fast')
            
        Returns:
            Image bytes or None if failed
        """
        model_name = self.models.get(model, self.models['fast'])
        
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'prompt': prompt,
            'num_steps': 20  # Balance between quality and speed
        }
        
        try:
            print(f"🎨 Generating image: {prompt[:60]}...")
            
            response = requests.post(
                f"{self.base_url}{model_name}",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                print(f"✅ Image generated successfully!")
                return response.content
            else:
                print(f"❌ Image generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            return None
    
    def generate_for_post(self, topic: str) -> Optional[bytes]:
        """
        Generate image optimized for social media post
        
        Args:
            topic: Post topic
            
        Returns:
            Image bytes ready for upload
        """
        prompt = self.generate_image_prompt(topic)
        return self.generate(prompt)


class FallbackImageGenerator:
    """Fallback using free placeholder/stock images"""
    
    @staticmethod
    def generate_placeholder(topic: str, width: int = 1200, height: int = 630) -> Optional[bytes]:
        """
        Generate placeholder image with topic text
        Uses a free service like placeholder.com or similar
        """
        try:
            # Simple colored placeholder with text
            url = f"https://placehold.co/{width}x{height}/2563eb/ffffff?text={topic[:50]}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"❌ Fallback image failed: {e}")
            return None


def create_image_generator() -> Optional[ImageGenerator]:
    """Factory function to create image generator"""
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    
    if account_id and api_token:
        return ImageGenerator(account_id, api_token)
    
    print("⚠️  Cloudflare credentials not found, image generation disabled")
    return None
