#!/usr/bin/env python3
"""
AI Social Bot - Main Script
Automatically generates and publishes tech content with AI images on Bluesky
"""

import sys
import os
import random
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from content.generator import ContentGenerator
from content.image_generator import create_image_generator, FallbackImageGenerator
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

def main(auto_mode=False, with_image=True):
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
    image_gen = create_image_generator() if with_image else None
    
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
        topic = random.choice(TOPICS)
        print(f"🤖 AUTO Mode - Topic chosen: {topic}")
    else:
        topic = input("📝 What topic to post about? (press Enter for default): ").strip()
        
        if not topic:
            topic = random.choice(TOPICS)
            print(f"📌 Topic chosen: {topic}")
    
    # 5. Generate content
    print("\n🤖 Generating content...")
    content = generator.generate_post(topic, platform="bluesky")
    
    # 6. Generate image (optional)
    image_bytes = None
    if with_image:
        if image_gen:
            print("\n🎨 Generating AI image...")
            image_bytes = image_gen.generate_for_post(topic)
            
            if not image_bytes:
                print("⚠️ AI image generation failed, trying fallback...")
                image_bytes = FallbackImageGenerator.generate_placeholder(topic)
        else:
            print("\n⚠️ Image generation disabled (Cloudflare credentials not found)")
    
    print("\n" + "="*50)
    print("📄 POST PREVIEW:")
    print("="*50)
    print(content)
    if image_bytes:
        print(f"🖼️  With AI-generated image ({len(image_bytes)} bytes)")
    print("="*50)
    print(f"📏 Length: {len(content)} characters")
    
    # 7. Confirm publication
    if auto_mode:
        confirm = 'y'
        print("\n🤖 AUTO Mode - Automatic publication")
    else:
        confirm = input("\n✅ Publish this post? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Publication cancelled.")
        return 0
    
    # 8. Publish!
    print("\n📤 Publishing...")
    result = bluesky.post(content, image_bytes=image_bytes)
    
    if result:
        # 9. Save to database
        db.save_post(
            content=content,
            platform="bluesky",
            post_url=result['url'],
            metadata={
                'topic': topic,
                'uri': result['uri'],
                'cid': result['cid'],
                'auto_mode': auto_mode,
                'has_image': result.get('has_image', False)
            }
        )
        
        print("\n" + "="*50)
        print("🎉 SUCCESS!")
        print("="*50)
        print(f"✅ Post published on Bluesky")
        print(f"🔗 URL: {result['url']}")
        if result.get('has_image'):
            print(f"🖼️  With AI-generated image")
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
    parser = argparse.ArgumentParser(description='AI Social Bot')
    parser.add_argument('--auto', action='store_true', 
                       help='Automatic mode (no user interaction)')
    parser.add_argument('--no-image', action='store_true',
                       help='Disable image generation')
    
    args = parser.parse_args()
    
    exit_code = main(auto_mode=args.auto, with_image=not args.no_image)
    sys.exit(exit_code)
