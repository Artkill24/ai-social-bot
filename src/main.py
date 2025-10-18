#!/usr/bin/env python3
"""
AI Social Bot - Main Script
Genera e pubblica contenuti automaticamente su Bluesky
"""

import sys
import os
import random
import argparse

# Aggiungi path per import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from content.generator import ContentGenerator
from platforms.bluesky import BlueskyPublisher
from utils.database import Database

# Lista topic predefiniti per modalità automatica
TOPICS = [
    "Come l'AI sta trasformando lo sviluppo software",
    "I migliori tool gratuiti per developers nel 2025",
    "Python vs JavaScript: quale imparare per AI",
    "GitHub Copilot e AI assistants: il futuro del coding",
    "Bluesky e il futuro delle piattaforme social decentralizzate",
    "Machine Learning accessibile: risorse gratuite per iniziare",
    "API gratuite che ogni developer dovrebbe conoscere",
    "Automazione con AI: risparmiare tempo nello sviluppo",
    "Open source AI models: alternative gratuite a ChatGPT",
    "Cloud computing gratuito per progetti AI",
    "Best practices per prompt engineering nel 2025",
    "Docker e containerizzazione: guida pratica",
    "Git workflows per team moderni",
    "Testing automation: strumenti essenziali",
    "CI/CD pipeline con GitHub Actions",
    "Database moderni: SQL vs NoSQL nel 2025",
    "Sicurezza web: le basi che ogni developer deve sapere",
    "Progressive Web Apps: quando e perché usarle",
    "Microservizi vs Monoliti: cosa scegliere",
    "Performance optimization: tips pratici",
]

def main(auto_mode=False):
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
        return 1
    
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
        return 1
    
    # 4. Scegli topic
    print("\n" + "="*50)
    
    if auto_mode:
        # Modalità automatica: scegli topic random
        topic = random.choice(TOPICS)
        print(f"🤖 Modalità AUTO - Topic scelto: {topic}")
    else:
        # Modalità manuale: chiedi all'utente
        topic = input("📝 Su che argomento vuoi postare? (premi Enter per default): ").strip()
        
        if not topic:
            topic = random.choice(TOPICS)
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
    if auto_mode:
        # Modalità auto: pubblica sempre
        confirm = 'y'
        print("\n🤖 Modalità AUTO - Pubblicazione automatica")
    else:
        # Modalità manuale: chiedi conferma
        confirm = input("\n✅ Pubblicare questo post? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Pubblicazione annullata.")
        return 0
    
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
                'cid': result['cid'],
                'auto_mode': auto_mode
            }
        )
        
        print("\n" + "="*50)
        print("🎉 SUCCESSO!")
        print("="*50)
        print(f"✅ Post pubblicato su Bluesky")
        print(f"🔗 URL: {result['url']}")
        print(f"💾 Salvato nel database")
        
        if auto_mode:
            print(f"🤖 Modalità automatica completata")
        else:
            print("\n🎊 Vai a vedere il post nel tuo profilo Bluesky!")
        
        return 0
    else:
        print("\n❌ Pubblicazione fallita. Controlla gli errori sopra.")
        return 1

if __name__ == "__main__":
    # Supporto argomenti da linea di comando
    parser = argparse.ArgumentParser(description='AI Social Bot')
    parser.add_argument('--auto', action='store_true', 
                       help='Modalità automatica (no interazione utente)')
    
    args = parser.parse_args()
    
    exit_code = main(auto_mode=args.auto)
    sys.exit(exit_code)
