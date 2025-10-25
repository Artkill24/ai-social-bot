#!/usr/bin/env python3
"""Monetization Dashboard"""
from src.growth.growth_engine import MonetizationEngine
from src.platforms.bluesky import BlueskyPublisher
from src.platforms.mastodon_publisher import MastodonPublisher
from config import Config

def main():
    print("\n" + "="*60)
    print("💰 MONETIZATION DASHBOARD")
    print("="*60)
    
    total_followers = 0
    
    if Config.ENABLE_BLUESKY:
        try:
            bluesky = BlueskyPublisher(Config.BLUESKY_USERNAME, Config.BLUESKY_PASSWORD)
            if bluesky.login():
                profile = bluesky.client.app.bsky.actor.get_profile({'actor': Config.BLUESKY_USERNAME})
                total_followers += profile.followers_count
                print(f"\n📘 Bluesky: {profile.followers_count} followers")
        except:
            print("\n📘 Bluesky: Unable to fetch")
    
    if Config.ENABLE_MASTODON:
        try:
            mastodon = MastodonPublisher(Config.MASTODON_INSTANCE_URL, Config.MASTODON_ACCESS_TOKEN)
            if mastodon.login():
                account = mastodon.client.account_verify_credentials()
                total_followers += account['followers_count']
                print(f"🐘 Mastodon: {account['followers_count']} followers")
        except:
            print("🐘 Mastodon: Unable to fetch")
    
    print(f"\n👥 TOTAL FOLLOWERS: {total_followers}")
    print("="*60)
    
    strategies = MonetizationEngine.get_available_strategies(total_followers)
    
    print("\n💡 MONETIZATION OPPORTUNITIES:\n")
    for strategy in strategies:
        status_emoji = "✅" if "Available" in strategy['status'] else "⏳"
        print(f"{status_emoji} {strategy['name'].upper()}")
        print(f"   Followers needed: {strategy['followers_needed']}")
        print(f"   Potential: {strategy['potential_monthly']}")
        print(f"   Status: {strategy['status']}")
        print(f"   {strategy['description']}\n")
    
    print("="*60)
    print("🚀 GROWTH TIPS:")
    print("   1. Post 2x daily (9AM, 5PM UTC)")
    print("   2. Run: python engage.py --max-posts 20")
    print("   3. Add affiliate links to bio")
    print("   4. Reply to comments fast")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
