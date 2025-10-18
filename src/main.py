#!/usr/bin/env python3
"""
AI Social Bot - Main Script
Genera e pubblica contenuti automaticamente su Bluesky
"""

import sys
import os

# Aggiungi path per import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from content.generator import ContentGenerator
from platforms.bluesky import BlueskyPublisher
from utils.database import Database

def main():
    """Script principale"""
    
    print("="*50)
    print("🤖 AI SOCIAL BOT - Avvio")
    print("="*50)
    
    # 1. Valida configurazione
    print("\n📋 Validazione credenziali...")
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n{e}")
        print("\n💡 Istruzioni:")
        print("   1. Copia .env.example → .env")
        print("   2. Ottieni Groq API key: console.groq.com")
        print("   3. Crea account Bluesky: bsky.app")
        print("   4. Compila .env con le tue credenziali")
        return
    
    # 2. Inizializza componenti
    print("\n🔧 Inizializzazione componenti...")
    
    db = Database(Config.DATABASE_PATH)
    generator = ContentGenerator(Config.GROQ_API_KEY)
    bluesky = BlueskyPublisher(
        Config.BLUESKY_USERNAME,
        Config.BLUESKY_PASSWORD
    )
    
    # 3. Login a Bluesky
    print("\n🔐 Login Bluesky...")
    if not bluesky.login():
        print("❌ Login fallito. Verifica credenziali in .env")
        return
    
    # 4. Chiedi topic o usa default
    print("\n" + "="*50)
    topic = input("📝 Su che argomento vuoi postare? (premi Enter per default): ").strip()
    
    if not topic:
        topics_default = [
            "Come l'AI sta cambiando il modo di programmare",
            "I migliori tool gratuiti per developers nel 2025",
            "Perché Python resta il linguaggio più amato",
            "GitHub Copilot vs Claude Code: quale scegliere?",
        ]
        import random
        topic = random.choice(topics_default)
        print(f"📌 Topic scelto: {topic}")
    
    # 5. Genera contenuto
    print("\n🤖 Generazione contenuto...")
    content = generator.generate_post(topic, platform="bluesky")
    
    print("\n" + "="*50)
    print("📄 PREVIEW DEL POST:")
    print("="*50)
    print(content)
    print("="*50)
    print(f"📏 Lunghezza: {len(content)} caratteri")
    
    # 6. Conferma pubblicazione
    confirm = input("\n✅ Pubblicare questo post? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Pubblicazione annullata.")
        return
    
    # 7. Pubblica!
    print("\n📤 Pubblicazione in corso...")
    result = bluesky.post(content)
    
    if result:
        # 8. Salva nel database
        db.save_post(
            content=content,
            platform="bluesky",
            post_url=result['url'],
            metadata={
                'topic': topic,
                'uri': result['uri'],
                'cid': result['cid']
            }
        )
        
        print("\n" + "="*50)
        print("🎉 SUCCESSO!")
        print("="*50)
        print(f"✅ Post pubblicato su Bluesky")
        print(f"🔗 URL: {result['url']}")
        print(f"💾 Salvato nel database")
        print("\n🎊 Vai a vedere il post nel tuo profilo Bluesky!")
    else:
        print("\n❌ Pubblicazione fallita. Controlla gli errori sopra.")

if __name__ == "__main__":
    main()
