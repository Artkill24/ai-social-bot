from groq import Groq
from typing import Optional
import random

class ContentGenerator:
    """Generates content using Groq AI (Llama 3.3 70B) - FREE!"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        
        # System prompts in English for variety
        self.system_prompts = [
            "You are a tech expert who explains complex concepts simply and accessibly. Use practical examples and effective analogies.",
            
            "You are an experienced developer sharing practical tips from the tech world. Your style is direct, technical but clear, focused on real applications.",
            
            "You are a tech enthusiast educating about AI, machine learning and innovation. Your tone is enthusiastic but professional, always fact-based.",
            
            "You are a tech educator making complex topics accessible. Use a step-by-step approach and never take anything for granted.",
            
            "You are a tech curator identifying and sharing the most interesting trends. You have a critical eye for meaningful innovation."
        ]
    
    def generate_post(self, 
                     topic: str, 
                     platform: str = "bluesky") -> str:
        """
        Generate a social media post on a specific topic
        
        Args:
            topic: The post topic
            platform: "bluesky" or "linkedin"
        
        Returns:
            Generated and validated post content
        """
        
        # Configure based on platform
        if platform == "bluesky":
            max_length = "280 characters (like Twitter)"
            format_tips = "1-2 strategic emojis, max 3 hashtags, conversational and authentic tone"
        else:
            max_length = "1200 characters"
            format_tips = "Strong hook, 3-5 bullet points, professional emojis, 3-5 hashtags"
        
        # Dynamic prompt in English
        user_prompt = f"""Write an educational {platform} post about:
        
TOPIC: {topic}

REQUIREMENTS:
- Maximum length: {max_length}
- Format: {format_tips}
- Educational and valuable
- Attention-grabbing hook
- Authentic, no clichés
- IMPORTANT: Write in English

Write ONLY the final post."""

        # Random system prompt for variety
        system_prompt = random.choice(self.system_prompts)
        
        try:
            # Call Groq API (FREE!)
            print(f"🤖 Generating content on: {topic[:50]}...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=600,
                top_p=0.9
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove quotes if present
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            
            # Check length for Bluesky
            if platform == "bluesky" and len(content) > 300:
                print(f"⚠️ Post too long ({len(content)} chars), shortening...")
                content = self._shorten_content(content)
            
            print(f"✅ Post generated: {len(content)} characters")
            return content
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return self._fallback_post(topic, platform)
    
    def _shorten_content(self, long_content: str) -> str:
        """Shorten content that's too long"""
        prompt = f"""Make this post more concise (max 280 characters):

{long_content}

Short version:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    def _fallback_post(self, topic: str, platform: str) -> str:
        """Emergency post if API fails"""
        return f"🤖 Today exploring: {topic}\n\nInsights coming soon! 💡\n\n#AI #Tech"
