from atproto import Client
from typing import Optional, Dict

class BlueskyPublisher:
    """Gestisce pubblicazione su Bluesky"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.client = None
        self.logged_in = False
    
    def login(self):
        """Effettua login a Bluesky"""
        try:
            print(f"🔐 Login a Bluesky come {self.username}...")
            
            self.client = Client()
            self.client.login(self.username, self.password)
            self.logged_in = True
            
            # Ottieni info profilo
            profile = self.client.app.bsky.actor.get_profile(
                {"actor": self.username}
            )
            
            print(f"✅ Login riuscito!")
            print(f"   👤 Handle: @{profile.handle}")
            print(f"   👥 Followers: {profile.followers_count}")
            print(f"   📝 Posts: {profile.posts_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore login Bluesky: {e}")
            print(f"   Verifica username e password in .env")
            self.logged_in = False
            return False
    
    def post(self, content: str) -> Optional[Dict]:
        """
        Pubblica un post su Bluesky
        
        Args:
            content: Il testo del post (max 300 caratteri)
        
        Returns:
            Dict con info del post, o None se errore
        """
        if not self.logged_in:
            if not self.login():
                return None
        
        # Verifica lunghezza
        if len(content) > 300:
            print(f"⚠️ Post troppo lungo ({len(content)}), trunco a 300")
            content = content[:297] + "..."
        
        try:
            print(f"📤 Pubblicando post su Bluesky...")
            
            # Pubblica il post
            response = self.client.send_post(text=content)
            
            # Costruisci URL del post
            post_id = response.uri.split('/')[-1]
            post_url = f"https://bsky.app/profile/{self.username}/post/{post_id}"
            
            result = {
                'success': True,
                'uri': response.uri,
                'cid': response.cid,
                'url': post_url,
                'indexed_at': str(response.indexed_at)
            }
            
            print(f"✅ Post pubblicato!")
            print(f"   🔗 URL: {post_url}")
            
            return result
            
        except Exception as e:
            print(f"❌ Errore pubblicazione: {e}")
            return None
