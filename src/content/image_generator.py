"""
Image Generator using Cloudflare Workers AI
Generates relevant images for social media posts using AI
"""

import requests
import os
from typing import Optional, Dict
import re
from PIL import Image
import io

class ImageGenerator:
    """Generates images using Cloudflare Workers AI with smart prompts"""
    
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
        """Generate a specific, relevant prompt based on the topic"""
        topic_lower = topic.lower()
        
        # Detailed prompt templates for specific topics
        prompts = {
            'ai': "futuristic artificial intelligence concept, glowing neural network nodes, blue and cyan digital particles, holographic interface, modern tech aesthetic, professional photography, 4k",
            
            'machine learning': "machine learning visualization, data points forming patterns, gradient blue to purple, abstract geometric shapes, modern minimalist design, professional tech illustration",
            
            'python': "Python programming language logo snake, clean code on dark screen, syntax highlighting in blue and yellow, modern developer workspace, minimalist tech aesthetic",
            
            'javascript': "JavaScript ES6 code on screen, colorful syntax highlighting, curly braces and functions visible, modern IDE interface, dark theme, professional developer setup",
            
            'coding': "software developer at modern workspace, multiple monitors with colorful code, clean desk setup, blue ambient lighting, professional photography, tech aesthetic",
            
            'github': "GitHub octocat logo, git branches visualization, version control flowchart, nodes and connections, dark theme, modern developer tools aesthetic",
            
            'docker': "Docker containers visualization, blue whale logo, shipping containers arranged in grid, modern DevOps concept, minimalist tech illustration",
            
            'cloud': "cloud computing infrastructure, servers and data centers connected by glowing lines, blue and white color scheme, modern technology concept art",
            
            'api': "API integration visualization, REST endpoints diagram, colorful data flow between systems, modern tech infographic style, clean design",
            
            'database': "database schema visualization, connected tables and relationships, organized data structure, blue and gray color scheme, professional database diagram",
            
            'security': "cybersecurity shield protecting digital data, encrypted connections, secure network visualization, blue and green secure aesthetic, modern tech concept",
            
            'web': "modern responsive website mockup on multiple devices, clean UI design, colorful interface, professional web design aesthetic",
            
            'react': "React component tree visualization, JSX code structure, modern frontend framework concept, blue React logo, clean tech illustration",
        }
        
        # Try to find best matching prompt
        best_match = None
        max_matches = 0
        
        for keyword, prompt in prompts.items():
            keyword_words = keyword.split()
            matches = sum(1 for word in keyword_words if word in topic_lower)
            
            if matches > max_matches:
                max_matches = matches
                best_match = prompt
        
        if best_match and max_matches > 0:
            return best_match
        
        # Default tech prompt
        return "modern technology concept, professional tech illustration, clean design, blue and purple gradient, minimalist aesthetic, 4k quality"
    
    def compress_image(self, image_bytes: bytes, max_size_kb: int = 800) -> bytes:
        """
        Compress image to reduce file size for faster upload
        
        Args:
            image_bytes: Original image bytes
            max_size_kb: Maximum size in KB (default 800KB for Bluesky)
            
        Returns:
            Compressed image bytes
        """
        try:
            # Open image
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large (max 1200x1200 for social media)
            max_dimension = 1200
            if img.width > max_dimension or img.height > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                print(f"   📐 Resized to {img.width}x{img.height}")
            
            # Compress with quality adjustment
            output = io.BytesIO()
            quality = 85
            
            while quality > 20:
                output.seek(0)
                output.truncate()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                size_kb = len(output.getvalue()) / 1024
                
                if size_kb <= max_size_kb:
                    break
                    
                quality -= 10
            
            compressed = output.getvalue()
            original_kb = len(image_bytes) / 1024
            compressed_kb = len(compressed) / 1024
            
            print(f"   🗜️  Compressed: {original_kb:.1f}KB → {compressed_kb:.1f}KB (quality: {quality})")
            
            return compressed
            
        except Exception as e:
            print(f"   ⚠️ Compression failed: {e}, using original")
            return image_bytes
    
    def generate(self, prompt: str, model: str = 'fast') -> Optional[bytes]:
        """Generate and compress image using Cloudflare Workers AI"""
        model_name = self.models.get(model, self.models['fast'])
        
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        # Enhanced prompt with quality boosters
        enhanced_prompt = f"{prompt}, professional photography, sharp focus, high quality, detailed"
        
        data = {
            'prompt': enhanced_prompt,
            'num_steps': 20
        }
        
        try:
            print(f"🎨 Generating image...")
            print(f"   Prompt: {prompt[:80]}...")
            
            response = requests.post(
                f"{self.base_url}{model_name}",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                original_size = len(response.content)
                print(f"✅ Image generated! ({original_size / 1024:.1f}KB)")
                
                # Compress before returning
                compressed = self.compress_image(response.content)
                return compressed
            else:
                print(f"❌ Generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            return None
    
    def generate_for_post(self, topic: str) -> Optional[bytes]:
        """Generate optimized image for social media post"""
        prompt = self.generate_image_prompt(topic)
        return self.generate(prompt)


class FallbackImageGenerator:
    """Fallback using tech-themed placeholder images"""
    
    @staticmethod
    def generate_placeholder(topic: str, width: int = 1200, height: int = 630) -> Optional[bytes]:
        """Generate tech-themed placeholder"""
        try:
            url = f"https://placehold.co/{width}x{height}/1e40af/60a5fa/png?text=Tech+Post&font=roboto"
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
