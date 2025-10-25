#!/usr/bin/env python3
"""Viral Mode - Ottimizzato per crescita"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from src.content.generator import ContentGenerator
from src.content.image_generator import create_image_generator
from src.platforms.bluesky import BlueskyPublisher
from src.platforms.mastodon_publisher import MastodonPublisher
from src.growth.growth_engine import ViralContentGenerator
from src.utils.database import Database
import random

VIRAL_TOPICS = [
    "AI tools that 10x productivity",
    "Free APIs every developer needs",
    "Python tricks nobody teaches",
    "GitHub secrets that save hours",
    "Free ChatGPT alternatives"
]

def main():
    print("🚀 VIRAL MODE")
    print("="*50)
    
    Config.validate()
    db = Database(Config.DATABASE_PATH)
    image_gen = create_image_generator()
    
    publishers = []
    if Config.ENABLE_BLUESKY:
        bluesky = BlueskyPublisher(Config.BLUESKY_USERNAME, Config.BLUESKY_PASSWORD)
        if bluesky.login():
            publishers.append(bluesky)
    
    if Config.ENABLE_MASTODON:
        mastodon = MastodonPublisher(Config.MASTODON_INSTANCE_URL, Config.MASTODON_ACCESS_TOKEN)
        if mastodon.login():
            publishers.append(mastodon)
    
    topic = random.choice(VIRAL_TOPICS)
    print(f"\n🎯 Topic: {topic}")
    
    content = ViralContentGenerator.generate_viral_post(topic)
    print(f"\n📝 Post:\n{content}\n")
    
    image_bytes = None
    if image_gen:
        image_bytes = image_gen.generate_for_post(topic)
    
    for publisher in publishers:
        result = publisher.post(content, image_bytes=image_bytes)
        if result:
            print(f"✅ Posted to {publisher.platform_name}")
            db.save_post(content, publisher.platform_name, result['url'], {'viral': True})
    
    print("\n🎉 Viral post published!")

if __name__ == "__main__":
    main()
