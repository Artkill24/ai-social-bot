"""
Image Generator using Cloudflare Workers AI
Generates relevant images for social media posts using AI
"""

import requests
import os
from typing import Optional
import re
from PIL import Image
import io

class ImageGenerator:
    """Generates images using Cloudflare Workers AI with smart prompts"""
    
    def __init__(self, account_id: str, api_token: str):
        self.account_id = account_id
        self.api_token = api_token
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/"
        
        self.models = {
            'stable-diffusion': '@cf/stabilityai/stable-diffusion-xl-base-1.0',
            'fast': '@cf/bytedance/stable-diffusion-xl-lightning'
        }
    
    def generate_image_prompt(self, topic: str) -> str:
        """Generate specific, relevant prompt based on topic"""
        topic_lower = topic.lower()
        
        # Enhanced prompts con più keyword
        prompts = {
            'ai': "futuristic artificial intelligence neural network, glowing blue nodes, holographic data visualization, modern tech aesthetic, professional photography, 4k",
            'machine learning': "machine learning algorithm visualization, colorful data patterns, gradient flow, abstract geometric shapes, modern tech illustration, high quality",
            'python': "Python programming code on screen, syntax highlighting, modern developer workspace, clean minimalist aesthetic, professional tech photography",
            'javascript': "JavaScript ES6 code, colorful syntax highlighting, modern IDE dark theme, web development aesthetic, professional setup",
            'coding': "software developer workspace, multiple monitors with code, modern tech setup, blue ambient lighting, professional photography",
            'programming': "clean code on screen, colorful syntax highlighting, modern developer environment, professional tech aesthetic",
            'github': "GitHub interface, git branches visualization, version control flowchart, dark theme, modern development tools",
            'docker': "Docker containers visualization, blue container architecture, modern DevOps concept, minimalist tech illustration",
            'kubernetes': "Kubernetes cluster architecture, container orchestration, blue and white K8s design, modern cloud infrastructure",
            'cloud': "cloud computing infrastructure, connected servers, glowing network lines, blue gradient, modern technology concept",
            'api': "REST API endpoints diagram, colorful data flow between systems, modern tech infographic, clean minimal design",
            'database': "database schema diagram, connected tables, organized data structure, blue and gray professional design",
            'sql': "SQL database visualization, table relationships, query optimization diagram, professional database design",
            'nosql': "NoSQL distributed database, document-based structure, modern data architecture, scalable design visualization",
            'security': "cybersecurity shield, encrypted data protection, secure network visualization, blue and green tech aesthetic",
            'blockchain': "blockchain network visualization, connected blocks, distributed ledger, blue and gold crypto design",
            'devops': "DevOps CI/CD pipeline, automated workflow diagram, modern infrastructure illustration, professional tech design",
            'web': "modern responsive website mockup, multiple devices, clean UI design, professional web aesthetic",
            'react': "React component architecture, JSX structure, modern frontend framework, blue logo, clean illustration",
            'angular': "Angular framework visualization, TypeScript code structure, modern web app design, red Angular theme",
            'vue': "Vue.js component tree, green Vue logo, modern frontend design, clean tech illustration",
            'node': "Node.js server architecture, JavaScript backend, event-driven design, green Node.js aesthetic",
            'testing': "automated testing dashboard, green checkmarks, code quality metrics, modern QA visualization",
            'agile': "agile sprint board, colorful kanban cards, scrum methodology, modern project management design",
            'git': "git workflow visualization, branch management, merge strategy diagram, modern version control design",
            'cicd': "CI/CD pipeline automation, build and deploy flow, modern DevOps workflow, professional illustration",
            'microservices': "microservices architecture, independent services connected via APIs, distributed system design",
            'serverless': "serverless cloud functions, event-driven architecture, modern cloud computing design",
            'mobile': "mobile app development, iOS and Android, responsive UI design, modern app interface",
            'frontend': "modern frontend development, HTML CSS JavaScript, responsive design, colorful UI components",
            'backend': "backend server infrastructure, database connections, API endpoints, professional architecture",
            'fullstack': "full stack development layers, frontend to backend, database integration, complete tech stack",
            'data': "data science visualization, colorful charts and graphs, statistical analysis, modern analytics",
            'analytics': "data analytics dashboard, metrics and KPIs, visualization charts, professional business intelligence",
            'prompt': "AI prompt engineering, natural language processing, neural network interface, modern AI interaction design",
        }
        
        # Multi-keyword matching
        best_prompt = None
        max_score = 0
        
        for keyword, prompt in prompts.items():
            # Score based on keyword presence
            keyword_words = keyword.split()
            score = sum(2 if word in topic_lower else 0 for word in keyword_words)
            
            # Bonus for exact keyword match
            if keyword in topic_lower:
                score += 5
            
            # Bonus for related terms
            if keyword == 'python' and any(w in topic_lower for w in ['programming', 'code', 'script']):
                score += 1
            if keyword == 'ai' and any(w in topic_lower for w in ['artificial', 'intelligence', 'machine', 'learning']):
                score += 1
            
            if score > max_score:
                max_score = score
                best_prompt = prompt
        
        if best_prompt and max_score > 0:
            return best_prompt
        
        # Fallback generico ma professionale
        return "modern technology concept, abstract digital visualization, blue and purple gradient, professional tech illustration, clean minimalist design, high quality"
    
    def compress_image(self, image_bytes: bytes, max_size_kb: int = 800) -> bytes:
        """Compress image for faster upload"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            max_dimension = 1200
            if img.width > max_dimension or img.height > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                print(f"   📐 Resized to {img.width}x{img.height}")
            
            # Compress
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
        """Generate and compress image"""
        model_name = self.models.get(model, self.models['fast'])
        
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
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
                
                compressed = self.compress_image(response.content)
                return compressed
            else:
                print(f"❌ Generation failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            return None
    
    def generate_for_post(self, topic: str) -> Optional[bytes]:
        """Generate optimized image for social media"""
        prompt = self.generate_image_prompt(topic)
        return self.generate(prompt)


class FallbackImageGenerator:
    """Fallback placeholder images"""
    
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
            print(f"❌ Fallback failed: {e}")
            return None


def create_image_generator() -> Optional[ImageGenerator]:
    """Factory function"""
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    
    if account_id and api_token:
        return ImageGenerator(account_id, api_token)
    
    print("⚠️  Cloudflare credentials not found")
    return None
