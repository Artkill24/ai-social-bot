import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    """Gestisce storage locale dei post e analytics"""
    
    def __init__(self, db_path: str = "data/posts.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Crea tabelle se non esistono"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella post pubblicati
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                platform TEXT NOT NULL,
                post_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Tabella trending topics (cache)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trending_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                source TEXT NOT NULL,
                url TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Database inizializzato")
    
    def save_post(self, content: str, platform: str, 
                  post_url: str = None, metadata: dict = None):
        """Salva un post pubblicato"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO posts (content, platform, post_url, metadata)
            VALUES (?, ?, ?, ?)
        """, (content, platform, post_url, json.dumps(metadata or {})))
        
        conn.commit()
        post_id = cursor.lastrowid
        conn.close()
        
        print(f"✅ Post salvato nel DB: ID {post_id}")
        return post_id
    
    def get_recent_posts(self, limit: int = 10) -> List[Dict]:
        """Recupera ultimi post pubblicati"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, content, platform, post_url, created_at
            FROM posts
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        posts = []
        for row in cursor.fetchall():
            posts.append({
                'id': row[0],
                'content': row[1],
                'platform': row[2],
                'url': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        return posts
