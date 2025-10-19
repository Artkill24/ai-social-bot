import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict

class DatabaseV2:
    """Database con analytics e metriche"""
    
    def __init__(self, db_path: str = "data/posts.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Crea schema completo con indici"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella post con metriche
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                platform TEXT NOT NULL,
                post_url TEXT,
                topic TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Metriche (aggiornate dopo)
                likes INTEGER DEFAULT 0,
                reshares INTEGER DEFAULT 0,
                replies INTEGER DEFAULT 0,
                last_metrics_update TIMESTAMP,
                
                -- Metadata
                metadata TEXT,
                
                -- Performance
                generation_time_ms INTEGER,
                char_count INTEGER,
                
                -- Status
                status TEXT DEFAULT 'published',
                error_log TEXT
            )
        """)
        
        # Indici per performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_platform_date 
            ON posts(platform, created_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_topic 
            ON posts(topic)
        """)
        
        # Tabella per tracciare duplicati
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_hashes (
                content_hash TEXT PRIMARY KEY,
                post_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def is_duplicate(self, content: str) -> bool:
        """Controlla se contenuto simile è già stato pubblicato"""
        import hashlib
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM content_hashes
            WHERE content_hash = ?
        """, (content_hash,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def get_analytics(self, days: int = 30) -> Dict:
        """Ottieni analytics degli ultimi N giorni"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_posts,
                AVG(likes) as avg_likes,
                AVG(reshares) as avg_reshares,
                AVG(char_count) as avg_length,
                platform,
                COUNT(DISTINCT topic) as unique_topics
            FROM posts
            WHERE created_at >= ?
            GROUP BY platform
        """, (since,))
        
        results = cursor.fetchall()
        conn.close()
        
        return {
            'period_days': days,
            'stats': [dict(zip([
                'total_posts', 'avg_likes', 'avg_reshares',
                'avg_length', 'platform', 'unique_topics'
            ], row)) for row in results]
        }
    
    def get_best_performing_topics(self, limit: int = 10) -> List[Dict]:
        """Trova i topic con migliori performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                topic,
                COUNT(*) as posts_count,
                AVG(likes + reshares * 2) as engagement_score,
                MAX(created_at) as last_used
            FROM posts
            WHERE topic IS NOT NULL
            GROUP BY topic
            ORDER BY engagement_score DESC
            LIMIT ?
        """, (limit,))
        
        topics = []
        for row in cursor.fetchall():
            topics.append({
                'topic': row[0],
                'posts_count': row[1],
                'engagement_score': row[2],
                'last_used': row[3]
            })
        
        conn.close()
        return topics
