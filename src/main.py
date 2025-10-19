#!/usr/bin/env python3
"""
AI Social Bot - Main Script
Automatically generates and publishes tech content on Bluesky
"""

import sys
import os
import random
import argparse

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from content.generator import ContentGenerator
from platforms.bluesky import BlueskyPublisher
from utils.database import Database

# Predefined topics for automatic mode - IN ENGLISH
TOPICS = [
    "How AI is transforming software development in 2025",
    "Best free tools for developers in 2025",
    "Python vs JavaScript: which to learn for AI",
    "GitHub Copilot and AI assistants: the future of coding",
    "Bluesky and the future of decentralized social platforms",
    "Accessible machine learning: free resources to get started",
    "Free APIs every developer should know",
    "Automation with AI: saving time in development",
    "Open source AI models: free alternatives to ChatGPT",
    "Free cloud computing for AI projects",
    "Best practices for prompt engineering in 2025",
    "Docker and containerization: practical guide",
    "Git workflows for modern teams",
    "Testing automation: essential tools",
    "CI/CD pipelines with GitHub Actions",
    "Modern databases: SQL vs NoSQL in 2025",
    "Web security: basics every developer must know",
    "Progressive Web Apps: when and why to use them",
    "Microservices vs Monoliths: what to choose",
    "Performance optimization: practical tips",
]

def main(auto_mode=False):
    """Main script"""
    
    print("="*50)
    print("🤖 AI SOCIAL BOT - Starting")
    print("="*50)
    
    # 1. Validate configuration
    print("\n📋 Validating credentials...")
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n{e}")
        print("\n💡 Instructions:")
        print("   1. Copy .env.example → .env")
        print("   2. Get Groq API key: console.groq.com")
        print("   3. Create Bluesky account: bsky.app")
        print("   4. Fill .env with your credentials")
        return 1
    
    # 2. Initialize components
    print("\n🔧 Initializing components...")
    
    db = Database(Config.DATABASE_PATH)
    generator = ContentGenerator(Config.GROQ_API_KEY)
    bluesky = BlueskyPublisher(
        Config.BLUESKY_USERNAME,
        Config.BLUESKY_PASSWORD
    )
    
    # 3. Login to Bluesky
    print("\n🔐 Bluesky Login...")
    if not bluesky.login():
        print("❌ Login failed. Check credentials in .env")
        return 1
    
    # 4. Choose topic
    print("\n" + "="*50)
    
    if auto_mode:
        # Automatic mode: choose random topic
        topic = random.choice(TOPICS)
        print(f"🤖 AUTO Mode - Topic chosen: {topic}")
    else:
        # Manual mode: ask user
        topic = input("📝 What topic to post about? (press Enter for default): ").strip()
        
        if not topic:
            topic = random.choice(TOPICS)
            print(f"📌 Topic chosen: {topic}")
    
    # 5. Generate content
    print("\n🤖 Generating content...")
    content = generator.generate_post(topic, platform="bluesky")
    
    print("\n" + "="*50)
    print("📄 POST PREVIEW:")
    print("="*50)
    print(content)
    print("="*50)
    print(f"📏 Length: {len(content)} characters")
    
    # 6. Confirm publication
    if auto_mode:
        # Auto mode: always publish
        confirm = 'y'
        print("\n🤖 AUTO Mode - Automatic publication")
    else:
        # Manual mode: ask confirmation
        confirm = input("\n✅ Publish this post? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Publication cancelled.")
        return 0
    
    # 7. Publish!
    print("\n📤 Publishing...")
    result = bluesky.post(content)
    
    if result:
        # 8. Save to database
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
        print("🎉 SUCCESS!")
        print("="*50)
        print(f"✅ Post published on Bluesky")
        print(f"🔗 URL: {result['url']}")
        print(f"💾 Saved to database")
        
        if auto_mode:
            print(f"🤖 Automatic mode completed")
        else:
            print("\n🎊 Go see the post on your Bluesky profile!")
        
        return 0
    else:
        print("\n❌ Publication failed. Check errors above.")
        return 1

if __name__ == "__main__":
    # Support command line arguments
    parser = argparse.ArgumentParser(description='AI Social Bot')
    parser.add_argument('--auto', action='store_true', 
                       help='Automatic mode (no user interaction)')
    
    args = parser.parse_args()
    
    exit_code = main(auto_mode=args.auto)
    sys.exit(exit_code)
