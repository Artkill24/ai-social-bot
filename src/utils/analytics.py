"""
Advanced Analytics for Social Bot
"""

import sqlite3
from typing import Dict, List
from datetime import datetime, timedelta

class Analytics:
    """Analytics engine for social bot performance"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_stats(self, days: int = 7) -> Dict:
        """Get comprehensive stats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Basic stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_posts,
                AVG(char_count) as avg_length,
                SUM(CASE WHEN platform = 'bluesky' THEN 1 ELSE 0 END) as bluesky_posts,
                SUM(CASE WHEN platform = 'linkedin' THEN 1 ELSE 0 END) as linkedin_posts,
                SUM(CASE WHEN has_hashtags = 1 THEN 1 ELSE 0 END) as posts_with_hashtags,
                SUM(CASE WHEN has_emojis = 1 THEN 1 ELSE 0 END) as posts_with_emojis
            FROM posts
            WHERE created_at >= ?
        """, (cutoff_date,))
        
        stats = cursor.fetchone()
        
        # Top topics
        cursor.execute("""
            SELECT topic, COUNT(*) as count
            FROM posts
            WHERE created_at >= ? AND topic IS NOT NULL
            GROUP BY topic
            ORDER BY count DESC
            LIMIT 5
        """, (cutoff_date,))
        
        top_topics = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_posts': stats[0] or 0,
            'avg_length': round(stats[1] or 0, 1),
            'bluesky_posts': stats[2] or 0,
            'linkedin_posts': stats[3] or 0,
            'posts_with_hashtags': stats[4] or 0,
            'posts_with_emojis': stats[5] or 0,
            'top_topics': top_topics,
            'period_days': days
        }
    
    def print_report(self, days: int = 7):
        """Print beautiful analytics report"""
        stats = self.get_stats(days)
        
        print("\n" + "="*50)
        print(f"📊 ANALYTICS REPORT - Last {days} Days")
        print("="*50)
        
        print(f"\n📝 Total Posts: {stats['total_posts']}")
        print(f"📏 Avg Length: {stats['avg_length']} chars")
        print(f"\n🌐 By Platform:")
        print(f"   📘 Bluesky: {stats['bluesky_posts']}")
        print(f"   💼 LinkedIn: {stats['linkedin_posts']}")
        
        print(f"\n🎨 Content Style:")
        print(f"   # Hashtags: {stats['posts_with_hashtags']} posts")
        print(f"   😊 Emojis: {stats['posts_with_emojis']} posts")
        
        if stats['top_topics']:
            print(f"\n🔥 Top Topics:")
            for i, (topic, count) in enumerate(stats['top_topics'], 1):
                print(f"   {i}. {topic[:50]}... ({count}x)")
        
        print("\n" + "="*50)
