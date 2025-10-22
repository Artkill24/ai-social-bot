#!/usr/bin/env python3
"""
AI Social Bot - Multi-Platform
Posts to Bluesky, LinkedIn, Mastodon automatically
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
from platforms.linkedin import LinkedInPublisher
from platforms.mastodon_publisher import MastodonPublisher
from utils.database import Database

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

def initialize_publishers():
    """Initialize all enabled social media publishers"""
    publishers = []
    
    # Bluesky
    if Config.ENABLE_BLUESKY and Config.BLUESKY_USERNAME and Config.BLUESKY_PASSWORD:
        publishers.append(BlueskyPublisher(
            Config.BLUESKY_USERNAME,
            Config.BLUESKY_PASSWORD
        ))
        print("📘 Bluesky enabled")
    
    # LinkedIn
    if Config.ENABLE_LINKEDIN and Config.LINKEDIN_ACCESS_TOKEN and Config.LINKEDIN_USER_ID:
        publishers.append(LinkedInPublisher(
            Config.LINKEDIN_ACCESS_TOKEN,
            Config.LINKEDIN_USER_ID
        ))
        print("💼 LinkedIn enabled")
    
    # Mastodon
    if Config.ENABLE_MASTODON and Config.MASTODON_ACCESS_TOKEN:
        publishers.append(MastodonPublisher(
            Config.MASTODON_INSTANCE_URL,
            Config.MASTODON_ACCESS_TOKEN
        ))
        print("🐘 Mastodon enabled")
    
    if not publishers:
        print("❌ No platforms enabled! Enable at least one in .env")
        return None
    
    return publishers

def main(auto_mode=False, with_image=True):
    """Main script - multi-platform"""
    
    print("="*50)
    print("🤖 AI SOCIAL BOT - Multi-Platform")
    print("="*50)
    
    # Validate
    print("\n📋 Validating credentials...")
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n{e}")
        return 1
    
    # Initialize
    print("\n🔧 Initializing components...")
    
    db = Database(Config.DATABASE_PATH)
    generator = ContentGenerator(Config.GROQ_API_KEY)
    image_gen = create_image_generator() if with_image else None
    publishers = initialize_publishers()
    
    if not publishers:
        return 1
    
    # Login to all platforms
    print("\n🔐 Logging into platforms...")
    active_publishers = []
    for publisher in publishers:
        if publisher.login():
            active_publishers.append(publisher)
        else:
            print(f"⚠️  {publisher.platform_name} login failed, skipping")
    
    if not active_publishers:
        print("❌ No platforms logged in successfully")
        return 1
    
    print(f"\n✅ {len(active_publishers)} platform(s) ready!")
    
    # Choose topic
    print("\n" + "="*50)
    
    if auto_mode:
        topic = random.choice(TOPICS)
        print(f"🤖 AUTO Mode - Topic: {topic}")
    else:
        topic = input("📝 Topic (Enter for random): ").strip()
        if not topic:
            topic = random.choice(TOPICS)
            print(f"📌 Topic: {topic}")
    
    # Generate content - adapt to longest platform
    max_length = max(p.max_length for p in active_publishers)
    print(f"\n🤖 Generating content (max {max_length} chars)...")
    content = generator.generate_post(topic, platform="bluesky")
    
    # Generate image
    image_bytes = None
    if with_image:
        if image_gen:
            print("\n🎨 Generating AI image...")
            image_bytes = image_gen.generate_for_post(topic)
            
            if not image_bytes:
                print("⚠️ AI image failed, trying fallback...")
                image_bytes = FallbackImageGenerator.generate_placeholder(topic)
        else:
            print("\n⚠️ Image generation disabled")
    
    # Preview
    print("\n" + "="*50)
    print("📄 POST PREVIEW:")
    print("="*50)
    print(content)
    if image_bytes:
        print(f"🖼️  With AI image ({len(image_bytes) / 1024:.1f}KB)")
    print("="*50)
    print(f"📏 Length: {len(content)} chars")
    print(f"🌐 Will post to: {', '.join(p.platform_name for p in active_publishers)}")
    
    # Confirm
    if auto_mode:
        confirm = 'y'
        print("\n🤖 AUTO Mode - Publishing automatically")
    else:
        confirm = input("\n✅ Publish to all platforms? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Cancelled")
        return 0
    
    # Publish to all platforms!
    print("\n📤 Publishing to all platforms...")
    results = []
    
    for publisher in active_publishers:
        print(f"\n📍 Publishing to {publisher.platform_name.upper()}...")
        result = publisher.post(content, image_bytes=image_bytes)
        
        if result:
            results.append(result)
            
            # Save to database
            db.save_post(
                content=content,
                platform=publisher.platform_name,
                post_url=result.get('url', ''),
                metadata={
                    'topic': topic,
                    'auto_mode': auto_mode,
                    'has_image': result.get('has_image', False),
                    **{k: v for k, v in result.items() if k not in ['success', 'platform']}
                }
            )
    
    # Summary
    print("\n" + "="*50)
    if results:
        print(f"🎉 SUCCESS! Posted to {len(results)}/{len(active_publishers)} platforms")
        print("="*50)
        for result in results:
            print(f"✅ {result['platform'].upper()}: {result.get('url', 'Posted')}")
            if result.get('has_image'):
                print(f"   🖼️  With AI image")
        print(f"💾 Saved to database")
        
        if auto_mode:
            print(f"🤖 Automatic mode completed")
        
        return 0
    else:
        print("❌ All platforms failed")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI Social Bot - Multi-Platform')
    parser.add_argument('--auto', action='store_true', 
                       help='Automatic mode')
    parser.add_argument('--no-image', action='store_true',
                       help='Disable images')
    
    args = parser.parse_args()
    
    exit_code = main(auto_mode=args.auto, with_image=not args.no_image)
    sys.exit(exit_code)
