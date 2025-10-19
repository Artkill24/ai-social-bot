import os
from dotenv import load_dotenv

# Carica variabili da .env
load_dotenv()

class Config:
    """Configurazione centralizzata per il bot"""
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Bluesky Credentials
    BLUESKY_USERNAME = os.getenv("BLUESKY_USERNAME")
    BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")
    
    # Reddit (opzionale per trending topics)
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    
    # Database
    DATABASE_PATH = "data/posts.db"
    
    # Impostazioni Bot
    POST_FREQUENCY_HOURS = 8
    MAX_POST_LENGTH = 280
    
    @classmethod
    def validate(cls):
        """Verifica che tutte le credenziali siano configurate"""
        required = {
            "GROQ_API_KEY": cls.GROQ_API_KEY,
            "BLUESKY_USERNAME": cls.BLUESKY_USERNAME,
            "BLUESKY_PASSWORD": cls.BLUESKY_PASSWORD
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(f"❌ Mancano queste credenziali: {', '.join(missing)}")
        
        print("✅ Tutte le credenziali configurate correttamente!")
        return True
