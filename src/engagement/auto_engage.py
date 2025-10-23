"""
Auto Engagement Engine
Automatically likes, boosts, and engages with relevant content
"""

import random
import time
from typing import List, Optional, Dict
from datetime import datetime

class EngagementEngine:
    """Manages automated engagement with other posts"""
    
    def __init__(self, publisher, target_hashtags: List[str] = None):
        self.publisher = publisher
        self.target_hashtags = target_hashtags or [
            '#AI', '#MachineLearning', '#Python', '#JavaScript',
            '#WebDev', '#DevTools', '#OpenSource', '#Programming',
            '#Docker', '#Kubernetes', '#CloudComputing', '#API'
        ]
        self.engaged_posts = set()
        self.daily_limit = {
            'likes': 50,
            'boosts': 10,
            'replies': 5
        }
        self.daily_count = {
            'likes': 0,
            'boosts': 0,
            'replies': 0
        }
    
    def should_engage(self, post: Dict) -> bool:
        """Decide if we should engage with this post"""
        if post.get('id') in self.engaged_posts:
            return False
        
        content = post.get('content', '').lower()
        has_target_hashtag = any(tag.lower() in content for tag in self.target_hashtags)
        
        if not has_target_hashtag:
            return False
        
        if len(content) < 50:
            return False
        
        hashtag_count = content.count('#')
        if hashtag_count > 10:
            return False
        
        return True
    
    def calculate_engagement_score(self, post: Dict) -> int:
        """Calculate how much we should engage (0-10)"""
        score = 5
        
        content = post.get('content', '').lower()
        
        matching_tags = sum(1 for tag in self.target_hashtags if tag.lower() in content)
        score += min(matching_tags, 3)
        
        if len(content) > 200:
            score += 1
        
        likes = post.get('favourites_count', 0)
        if likes > 10:
            score += 1
        
        return min(score, 10)
    
    def like_post(self, post_id: str) -> bool:
        """Like a post"""
        if self.daily_count['likes'] >= self.daily_limit['likes']:
            print("⚠️  Daily like limit reached")
            return False
        
        try:
            if hasattr(self.publisher, 'client'):
                self.publisher.client.status_favourite(post_id)
            
            self.engaged_posts.add(post_id)
            self.daily_count['likes'] += 1
            print(f"❤️  Liked post {post_id[:8]}...")
            return True
        except Exception as e:
            print(f"❌ Like failed: {e}")
            return False
    
    def boost_post(self, post_id: str) -> bool:
        """Boost/Repost a post"""
        if self.daily_count['boosts'] >= self.daily_limit['boosts']:
            print("⚠️  Daily boost limit reached")
            return False
        
        try:
            if hasattr(self.publisher, 'client'):
                self.publisher.client.status_reblog(post_id)
            
            self.engaged_posts.add(post_id)
            self.daily_count['boosts'] += 1
            print(f"🔄 Boosted post {post_id[:8]}...")
            return True
        except Exception as e:
            print(f"❌ Boost failed: {e}")
            return False
    
    def auto_engage_session(self, max_posts: int = 20):
        """Run an auto-engagement session"""
        print("\n🤖 Starting auto-engagement session...")
        print(f"🎯 Target hashtags: {', '.join(self.target_hashtags[:5])}...")
        
        engaged_count = 0
        
        try:
            for hashtag in self.target_hashtags[:3]:
                print(f"\n🔍 Searching posts with {hashtag}...")
                
                if hasattr(self.publisher, 'client'):
                    results = self.publisher.client.timeline_hashtag(
                        hashtag.replace('#', ''),
                        limit=10
                    )
                    
                    for post in results:
                        if engaged_count >= max_posts:
                            break
                        
                        if not self.should_engage(post):
                            continue
                        
                        score = self.calculate_engagement_score(post)
                        
                        if score >= 5:
                            if self.like_post(post['id']):
                                engaged_count += 1
                                time.sleep(random.uniform(2, 5))
                        
                        if score >= 8:
                            if self.boost_post(post['id']):
                                engaged_count += 1
                                time.sleep(random.uniform(3, 6))
                
                time.sleep(random.uniform(5, 10))
        
        except Exception as e:
            print(f"❌ Engagement session error: {e}")
        
        print(f"\n✅ Engagement session complete!")
        print(f"   ❤️  Likes: {self.daily_count['likes']}/{self.daily_limit['likes']}")
        print(f"   🔄 Boosts: {self.daily_count['boosts']}/{self.daily_limit['boosts']}")
        print(f"   💬 Replies: {self.daily_count['replies']}/{self.daily_limit['replies']}")
        
        return engaged_count


class SmartReplies:
    """Generate contextual replies to posts"""
    
    REPLY_TEMPLATES = [
        "Great insight! 🚀",
        "This is really helpful, thanks for sharing! 💡",
        "Interesting perspective! 🤔",
        "Love this approach! 👏",
        "Saved for later reference! 📚",
    ]
    
    @staticmethod
    def generate_reply(post_content: str) -> str:
        """Generate a contextual reply"""
        return random.choice(SmartReplies.REPLY_TEMPLATES)
