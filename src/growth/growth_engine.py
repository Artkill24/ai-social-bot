"""
Growth Engine - Strategie per crescita e monetizzazione
"""
import random
from typing import List, Dict
from datetime import datetime, timedelta

class GrowthEngine:
    """Engine per crescita organica rapida"""
    
    BEST_POSTING_TIMES = [(9, 0), (12, 0), (17, 0), (20, 0)]
    
    VIRAL_HASHTAGS = {
        'high_volume': ['#AI', '#Tech', '#Programming', '#WebDev'],
        'medium_volume': ['#100DaysOfCode', '#DevCommunity', '#BuildInPublic'],
        'niche': ['#AIAutomation', '#FreeTech', '#OpenSourceAI']
    }
    
    @staticmethod
    def optimize_hashtags(topic: str) -> List[str]:
        """Mix strategico di hashtag"""
        hashtags = []
        hashtags.extend(random.sample(GrowthEngine.VIRAL_HASHTAGS['high_volume'], 2))
        hashtags.extend(random.sample(GrowthEngine.VIRAL_HASHTAGS['medium_volume'], 2))
        hashtags.extend(random.sample(GrowthEngine.VIRAL_HASHTAGS['niche'], 1))
        return hashtags

class MonetizationEngine:
    """Sistema per monetizzazione"""
    
    MONETIZATION_STRATEGIES = {
        'affiliate_marketing': {
            'followers_needed': 100,
            'potential_monthly': '$50-200',
            'description': 'Share affiliate links'
        },
        'sponsored_posts': {
            'followers_needed': 1000,
            'potential_monthly': '$200-1000',
            'description': 'Paid mentions'
        },
        'consulting': {
            'followers_needed': 500,
            'potential_monthly': '$500-5000',
            'description': 'AI consulting'
        }
    }
    
    @staticmethod
    def get_available_strategies(current_followers: int) -> List[Dict]:
        """Strategie disponibili"""
        available = []
        for name, strategy in MonetizationEngine.MONETIZATION_STRATEGIES.items():
            if current_followers >= strategy['followers_needed']:
                strategy['status'] = '✅ Available'
            else:
                needed = strategy['followers_needed'] - current_followers
                strategy['status'] = f'⏳ Need {needed} more'
            available.append({'name': name, **strategy})
        return available

class ViralContentGenerator:
    """Genera contenuti virali"""
    
    @staticmethod
    def generate_viral_post(topic: str) -> str:
        """Genera post virale"""
        hooks = [
            f"🚨 This {topic} trick saved me 10 hours/week",
            f"Free {topic} resource that changed everything",
            f"Most devs ignore this {topic} hack"
        ]
        hook = random.choice(hooks)
        
        content = "Here's what worked:\n✅ Simple\n✅ Free\n✅ Fast results"
        cta = "\n\n💾 Bookmark this\n♻️ Share if useful"
        hashtags = ' '.join(GrowthEngine.optimize_hashtags(topic))
        
        return f"{hook}\n\n{content}{cta}\n\n{hashtags}"

class GrowthAnalytics:
    """Analytics di crescita"""
    
    @staticmethod
    def calculate_growth_rate(followers_history: List[Dict]) -> Dict:
        """Calcola tasso di crescita"""
        if len(followers_history) < 2:
            return {'daily_rate': 0, 'projection': 0}
        
        recent = followers_history[-7:]
        if len(recent) >= 2:
            daily = (recent[-1]['followers'] - recent[0]['followers']) / len(recent)
        else:
            daily = 0
        
        current = followers_history[-1]['followers']
        projection = current + (daily * 30)
        
        return {
            'daily_rate': round(daily, 2),
            'monthly_projection': int(projection),
            'days_to_1k': int((1000 - current) / daily) if daily > 0 else 'N/A'
        }
