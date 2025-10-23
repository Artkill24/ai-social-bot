#!/usr/bin/env python3
"""
Auto-engagement script for social bot
"""

import sys
import argparse
from src.engagement.auto_engage import EngagementEngine
from src.platforms.mastodon_publisher import MastodonPublisher
from config import Config

def main():
    parser = argparse.ArgumentParser(description='Auto-engage with relevant posts')
    parser.add_argument('--max-posts', type=int, default=10, help='Max posts to engage with')
    parser.add_argument('--hashtags', type=str, help='Comma-separated hashtags')
    args = parser.parse_args()
    
    print("🤖 Auto-Engagement Mode")
    print("="*50)
    
    if not Config.ENABLE_MASTODON or not Config.MASTODON_ACCESS_TOKEN:
        print("❌ Mastodon not configured!")
        return
    
    publisher = MastodonPublisher(
        Config.MASTODON_INSTANCE_URL,
        Config.MASTODON_ACCESS_TOKEN
    )
    
    if not publisher.login():
        print("❌ Mastodon login failed!")
        return
    
    hashtags = args.hashtags.split(',') if args.hashtags else None
    engine = EngagementEngine(publisher, target_hashtags=hashtags)
    engaged = engine.auto_engage_session(max_posts=args.max_posts)
    
    print(f"\n✅ Engaged with {engaged} posts!")

if __name__ == "__main__":
    main()
