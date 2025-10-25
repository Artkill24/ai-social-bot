"""
Auto-Reply Engine - Risponde automaticamente a commenti e menzioni
"""

import random
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class AutoReplyEngine:
    """Engine per risposte automatiche intelligenti"""
    
    def __init__(self, content_generator, publisher):
        self.generator = content_generator
        self.publisher = publisher
        self.replied_to = set()  # Track già risposti
        self.daily_reply_limit = 50
        self.daily_reply_count = 0
        
    def should_reply(self, comment: Dict) -> bool:
        """Decide se rispondere"""
        comment_id = comment.get('id')
        
        # Skip se già risposto
        if comment_id in self.replied_to:
            return False
        
        # Skip se limite giornaliero raggiunto
        if self.daily_reply_count >= self.daily_reply_limit:
            return False
        
        # Skip commenti troppo corti (probabilmente spam)
        text = comment.get('content', '')
        if len(text.strip()) < 10:
            return False
        
        # Skip se è il nostro stesso commento
        author = comment.get('account', {}).get('username', '')
        if author in ['tech_curator_ai', 'tech-curator-ai']:
            return False
        
        return True
    
    def generate_contextual_reply(self, comment_text: str, original_post: str) -> str:
        """Genera risposta contestuale usando AI"""
        
        # Prompt per Groq
        prompt = f"""Generate a friendly, helpful reply to this comment on our tech post.

Original Post: "{original_post[:200]}..."

Comment: "{comment_text}"

Generate a short (1-2 sentences), genuine reply that:
- Thanks them for engaging
- Adds value or answers their question
- Is casual and friendly
- Includes a relevant emoji
- NO hashtags in replies

Reply:"""
        
        try:
            response = self.generator.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=100,
                temperature=0.7
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Cleanup
            reply = reply.replace('"', '').replace('\n', ' ').strip()
            
            # Limit length
            if len(reply) > 280:
                reply = reply[:277] + "..."
            
            return reply
            
        except Exception as e:
            print(f"⚠️  AI reply generation failed: {e}")
            return self._get_fallback_reply(comment_text)
    
    def _get_fallback_reply(self, comment_text: str) -> str:
        """Risposte di fallback se AI non disponibile"""
        
        comment_lower = comment_text.lower()
        
        # Question
        if '?' in comment_text:
            replies = [
                "Great question! 🤔 Check out the resources in my bio for more details!",
                "Good point! 💡 I'll cover this in more depth soon. Stay tuned!",
                "Thanks for asking! 👍 This is exactly the kind of thing I'm exploring.",
            ]
        # Thanks/Positive
        elif any(word in comment_lower for word in ['thanks', 'thank', 'helpful', 'great', 'awesome']):
            replies = [
                "Glad you found it helpful! 🙏 More content coming soon!",
                "You're welcome! 😊 Let me know if you have questions!",
                "Happy to help! 🚀 Feel free to reach out anytime!",
            ]
        # Negative/Criticism
        elif any(word in comment_lower for word in ['wrong', 'disagree', 'not sure']):
            replies = [
                "Thanks for the feedback! 🤝 Always open to different perspectives.",
                "Interesting point! 💭 Would love to hear more about your approach.",
                "Appreciate your input! 👍 Different tools work for different needs.",
            ]
        # Request for more
        elif any(word in comment_lower for word in ['more', 'tutorial', 'guide', 'how']):
            replies = [
                "Absolutely! 📚 Check my bio for detailed guides and resources!",
                "Great idea! 💡 I'll create content on this soon. Follow for updates!",
                "Coming soon! 🚀 Subscribe to stay notified when I post it!",
            ]
        # Default
        else:
            replies = [
                "Thanks for engaging! 🙏 Appreciate your thoughts!",
                "Glad you're interested! 😊 More content like this coming!",
                "Thanks for sharing! 💭 Love hearing from the community!",
                "Appreciate the comment! 🤝 Let's keep the conversation going!",
            ]
        
        return random.choice(replies)
    
    def reply_to_comment(self, comment: Dict, original_post: str) -> bool:
        """Risponde a un commento"""
        
        if not self.should_reply(comment):
            return False
        
        try:
            comment_id = comment['id']
            comment_text = comment.get('content', '').strip()
            author = comment.get('account', {}).get('username', 'friend')
            
            print(f"\n💬 Replying to @{author}: {comment_text[:50]}...")
            
            # Genera risposta contestuale
            reply_text = self.generate_contextual_reply(comment_text, original_post)
            
            # Post reply
            if hasattr(self.publisher, 'client'):  # Mastodon
                self.publisher.client.status_post(
                    reply_text,
                    in_reply_to_id=comment_id,
                    visibility='public'
                )
            elif hasattr(self.publisher, 'reply'):  # Bluesky (se implementato)
                self.publisher.reply(comment_id, reply_text)
            
            self.replied_to.add(comment_id)
            self.daily_reply_count += 1
            
            print(f"✅ Replied: {reply_text}")
            
            # Human-like delay
            time.sleep(random.uniform(5, 15))
            
            return True
            
        except Exception as e:
            print(f"❌ Reply failed: {e}")
            return False
    
    def auto_follow_back(self, account_id: str) -> bool:
        """Follow back automatico per chi interagisce"""
        try:
            if hasattr(self.publisher, 'client'):  # Mastodon
                # Check se già following
                relationship = self.publisher.client.account_relationships(account_id)[0]
                if not relationship['following']:
                    self.publisher.client.account_follow(account_id)
                    print(f"👥 Followed back account {account_id}")
                    return True
            return False
        except Exception as e:
            print(f"⚠️  Follow back failed: {e}")
            return False
    
    def monitor_and_reply(self, max_replies: int = 20):
        """Monitora e risponde a commenti recenti"""
        print("\n🤖 Auto-Reply Session Started...")
        print("="*50)
        
        replies_count = 0
        follows_count = 0
        
        try:
            # Get our recent posts
            if hasattr(self.publisher, 'client'):  # Mastodon
                # Get account info
                account = self.publisher.client.account_verify_credentials()
                account_id = account['id']
                
                # Get notifications (mentions, replies)
                notifications = self.publisher.client.notifications(
                    limit=40,
                    types=['mention', 'favourite', 'reblog']
                )
                
                for notif in notifications:
                    if replies_count >= max_replies:
                        break
                    
                    notif_type = notif['type']
                    notif_account = notif['account']
                    
                    # Auto follow back chi fa like/reblog
                    if notif_type in ['favourite', 'reblog']:
                        if self.auto_follow_back(notif_account['id']):
                            follows_count += 1
                    
                    # Reply to mentions
                    if notif_type == 'mention':
                        status = notif['status']
                        
                        # Get original post context
                        original_post = ""
                        if status.get('in_reply_to_id'):
                            try:
                                original = self.publisher.client.status(status['in_reply_to_id'])
                                original_post = original.get('content', '')
                            except:
                                original_post = "tech topic"
                        
                        if self.reply_to_comment(status, original_post):
                            replies_count += 1
        
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
        
        print("\n" + "="*50)
        print(f"✅ Auto-Reply Session Complete!")
        print(f"   💬 Replies sent: {replies_count}")
        print(f"   👥 Follow-backs: {follows_count}")
        print("="*50 + "\n")
        
        return replies_count


class SmartMentionFinder:
    """Trova opportunità per menzionare il bot"""
    
    @staticmethod
    def find_relevant_conversations(publisher, keywords: List[str]) -> List[Dict]:
        """Trova conversazioni rilevanti dove partecipare"""
        relevant = []
        
        try:
            if hasattr(publisher, 'client'):  # Mastodon
                # Search per keyword
                for keyword in keywords[:3]:
                    results = publisher.client.timeline_hashtag(
                        keyword.replace('#', ''),
                        limit=20
                    )
                    
                    for post in results:
                        # Skip if no engagement
                        if post.get('replies_count', 0) < 2:
                            continue
                        
                        # Skip if too old
                        created = post.get('created_at')
                        if created:
                            age = datetime.now(created.tzinfo) - created
                            if age > timedelta(hours=24):
                                continue
                        
                        relevant.append(post)
        
        except Exception as e:
            print(f"⚠️  Search error: {e}")
        
        return relevant[:10]
