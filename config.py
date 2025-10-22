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

    # Cloudflare for AI Image Generation
    CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

    # LinkedIn Credentials (Optional)
    LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
    LINKEDIN_USER_ID = os.getenv("LINKEDIN_USER_ID")

    # Mastodon Credentials (Optional)
    MASTODON_INSTANCE_URL = os.getenv("MASTODON_INSTANCE_URL", "https://mastodon.social")
    MASTODON_ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")

    # Reddit (opzionale per trending topics)
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

    # Database
    DATABASE_PATH = "data/posts.db"

    # Impostazioni Bot
    POST_FREQUENCY_HOURS = 8
    MAX_POST_LENGTH = 280

    # Platform toggles
    ENABLE_BLUESKY = os.getenv("ENABLE_BLUESKY", "true").lower() == "true"
    ENABLE_LINKEDIN = os.getenv("ENABLE_LINKEDIN", "false").lower() == "true"
    ENABLE_MASTODON = os.getenv("ENABLE_MASTODON", "false").lower() == "true"

    @classmethod
    def validate(cls):
        """Valida che tutte le credenziali necessarie siano presenti"""
        missing = []
        
        if not cls.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        
        # Check Bluesky se abilitato
        if cls.ENABLE_BLUESKY:
            if not cls.BLUESKY_USERNAME:
                missing.append("BLUESKY_USERNAME")
            if not cls.BLUESKY_PASSWORD:
                missing.append("BLUESKY_PASSWORD")
        
        # Check LinkedIn se abilitato
        if cls.ENABLE_LINKEDIN:
            if not cls.LINKEDIN_ACCESS_TOKEN:
                missing.append("LINKEDIN_ACCESS_TOKEN")
            if not cls.LINKEDIN_USER_ID:
                missing.append("LINKEDIN_USER_ID")
        
        # Check Mastodon se abilitato
        if cls.ENABLE_MASTODON:
            if not cls.MASTODON_ACCESS_TOKEN:
                missing.append("MASTODON_ACCESS_TOKEN")
        
        if missing:
            raise ValueError(
                f"❌ Credenziali mancanti: {', '.join(missing)}\n"
                f"   Configurale nel file .env"
            )
        
        print("✅ Tutte le credenziali configurate correttamente!")
        return True
