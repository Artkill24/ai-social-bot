from typing import Dict
from datetime import datetime

class HealthChecker:
    """Verifica salute sistema e servizi"""
    
    @staticmethod
    def check_groq_api(api_key: str) -> Dict:
        """Verifica che Groq API sia raggiungibile"""
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return {"status": "healthy", "service": "groq"}
        except Exception as e:
            return {"status": "unhealthy", "service": "groq", "error": str(e)}
    
    @staticmethod
    def check_bluesky_api(username: str, password: str) -> Dict:
        """Verifica connessione Bluesky"""
        try:
            from atproto import Client
            client = Client()
            client.login(username, password)
            return {"status": "healthy", "service": "bluesky"}
        except Exception as e:
            return {"status": "unhealthy", "service": "bluesky", "error": str(e)}
    
    @staticmethod
    def run_all_checks(config) -> Dict:
        """Esegui tutti i check"""
        checks = {
            "groq": HealthChecker.check_groq_api(config.GROQ_API_KEY),
            "bluesky": HealthChecker.check_bluesky_api(
                config.BLUESKY_USERNAME,
                config.BLUESKY_PASSWORD
            )
        }
        
        all_healthy = all(c["status"] == "healthy" for c in checks.values())
        
        return {
            "overall_status": "healthy" if all_healthy else "degraded",
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }
