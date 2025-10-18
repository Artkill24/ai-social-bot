from groq import Groq
from typing import Optional
import random

class ContentGenerator:
    """Genera contenuti usando Groq AI (Llama 3.1 70B) - GRATIS!"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-70b-versatile"
        
        # Template di system prompts per varietà
        self.system_prompts = [
            "Sei un esperto di tecnologia che spiega concetti complessi in modo semplice.",
            "Sei un developer che condivide tips pratici dal mondo tech.",
            "Sei un enthusiast AI che educa su machine learning e innovazione."
        ]
    
    def generate_post(self, 
                     topic: str, 
                     platform: str = "bluesky") -> str:
        """
        Genera un post social su un topic specifico
        
        Args:
            topic: L'argomento del post
            platform: "bluesky" o "linkedin"
        
        Returns:
            Il contenuto del post generato
        """
        
        # Configura lunghezza basata su piattaforma
        if platform == "bluesky":
            max_length = "280 caratteri (come Twitter)"
            format_tips = "Usa 1-2 emoji, 1-2 hashtag, tono conversazionale"
        else:
            max_length = "1200 caratteri"
            format_tips = "Hook forte, bullet points, emoji strategici"
        
        # Prompt dinamico
        user_prompt = f"""Scrivi un post {platform} educativo su:
        
TOPIC: {topic}

REQUISITI:
- Lunghezza massima: {max_length}
- {format_tips}
- Educativo e di valore
- Hook che cattura attenzione
- Autentico, no cliché

Scrivi SOLO il post finale."""

        # System prompt randomico per varietà
        system_prompt = random.choice(self.system_prompts)
        
        try:
            # Chiamata a Groq API (GRATIS!)
            print(f"🤖 Generando contenuto su: {topic[:50]}...")
            
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
            
            # Verifica lunghezza per Bluesky
            if platform == "bluesky" and len(content) > 300:
                print(f"⚠️ Post troppo lungo ({len(content)} char), accorcio...")
                content = self._shorten_content(content)
            
            print(f"✅ Post generato: {len(content)} caratteri")
            return content
            
        except Exception as e:
            print(f"❌ Errore generazione: {e}")
            return self._fallback_post(topic, platform)
    
    def _shorten_content(self, long_content: str) -> str:
        """Accorcia contenuto troppo lungo"""
        prompt = f"""Rendi questo post più conciso (max 280 caratteri):

{long_content}

Versione corta:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    def _fallback_post(self, topic: str, platform: str) -> str:
        """Post di emergenza se API fallisce"""
        return f"🤖 Oggi esploro: {topic}\n\nInsights in arrivo! 💡\n\n#AI #Tech"
