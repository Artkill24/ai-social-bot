import feedparser
import requests
from typing import List, Dict
from datetime import datetime

class TrendingFinder:
    """Trova trending topics da varie fonti"""
    
    @staticmethod
    def get_hackernews_trends(limit: int = 10) -> List[Dict]:
        """Ottieni top stories da HackerNews"""
        try:
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = requests.get(url, timeout=10)
            story_ids = response.json()[:limit]
            
            stories = []
            for story_id in story_ids:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_data = requests.get(story_url, timeout=5).json()
                
                if story_data and 'title' in story_data:
                    stories.append({
                        'title': story_data['title'],
                        'url': story_data.get('url', ''),
                        'score': story_data.get('score', 0),
                        'source': 'hackernews'
                    })
            
            return sorted(stories, key=lambda x: x['score'], reverse=True)
            
        except Exception as e:
            print(f"❌ Errore HackerNews: {e}")
            return []
    
    @staticmethod
    def get_dev_to_trends(limit: int = 10) -> List[Dict]:
        """Ottieni trending da Dev.to"""
        try:
            url = "https://dev.to/api/articles?top=7"
            response = requests.get(url, timeout=10)
            articles = response.json()[:limit]
            
            return [{
                'title': article['title'],
                'url': article['url'],
                'score': article.get('public_reactions_count', 0),
                'source': 'dev.to',
                'tags': article.get('tag_list', [])
            } for article in articles]
            
        except Exception as e:
            print(f"❌ Errore Dev.to: {e}")
            return []
    
    @staticmethod
    def combine_trends(sources: List[str] = None) -> List[str]:
        """Combina trends da multiple fonti"""
        if sources is None:
            sources = ['hackernews', 'devto']
        
        all_trends = []
        
        if 'hackernews' in sources:
            all_trends.extend(TrendingFinder.get_hackernews_trends())
        
        if 'devto' in sources:
            all_trends.extend(TrendingFinder.get_dev_to_trends())
        
        # Estrai titoli unici
        unique_titles = list(set(t['title'] for t in all_trends))
        
        return unique_titles[:20]
