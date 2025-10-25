#!/usr/bin/env python3
"""
Auto-Reply Bot - Risponde automaticamente a commenti e menzioni
"""

import sys
import argparse
from src.engagement.auto_reply import AutoReplyEngine
from src.content.generator import ContentGenerator
from src.platforms.mastodon_publisher import MastodonPublisher
from src.platforms.bluesky import BlueskyPublisher
from config import Config

def main():
    parser = argparse.ArgumentParser(description='Auto-reply to comments and mentions')
    parser.add_argument('--platform', type=str, default='mastodon', 
                       help='Platform (mastodon/bluesky)')
    parser.add_argument('--max-replies', type=int, default=20,
                       help='Max replies per session')
    args = parser.parse_args()
    
    print("\n🤖 AUTO-REPLY BOT")
    print("="*60)
    
    # Setup content generator for AI replies
    generator = ContentGenerator(Config.GROQ_API_KEY)
    
    # Setup publisher
    if args.platform == 'mastodon':
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
    
    elif args.platform == 'bluesky':
        if not Config.ENABLE_BLUESKY:
            print("❌ Bluesky not configured!")
            return
        
        publisher = BlueskyPublisher(
            Config.BLUESKY_USERNAME,
            Config.BLUESKY_PASSWORD
        )
        if not publisher.login():
            print("❌ Bluesky login failed!")
            return
    
    else:
        print(f"❌ Unknown platform: {args.platform}")
        return
    
    # Run auto-reply
    reply_engine = AutoReplyEngine(generator, publisher)
    reply_engine.monitor_and_reply(max_replies=args.max_replies)
    
    print("\n✅ Auto-reply session complete!")
    print("\n💡 Pro tip: Run this every 2-3 hours for best engagement!")

if __name__ == "__main__":
    main()
