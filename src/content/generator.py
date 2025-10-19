"""
Content Generator - Generazione intelligente di contenuti social
Utilizza Groq AI (Llama 3.3 70B) per creare post educativi e di valore
"""

from groq import Groq
from typing import Optional, Dict, List, Tuple
import random
import time
import logging
from functools import wraps

# Setup logger
logger = logging.getLogger(__name__)


class ContentValidator:
    """Valida qualità, sicurezza e compliance del contenuto generato"""
    
    # Lista parole/frasi bannate (espandi in base alle tue policy)
    BANNED_WORDS = [
        'spam', 'scam', 'pump and dump', 'get rich quick',
        'guarantee', 'free money', 'click here', 'buy now',
        'limited time', 'act now', 'exclusive deal'
    ]
    
    # Pattern sospetti
    SUSPICIOUS_PATTERNS = [
        r'http[s]?://bit\.ly',  # Link abbreviati sospetti
        r'\$\$\$',  # Simboli monetari ripetuti
        r'!!!+',   # Troppi punti esclamativi
    ]
    
    # Limiti di qualità
    MIN_LENGTH = 50
    MAX_LENGTH = 300  # Per Bluesky
    MAX_EMOJI_COUNT = 5
    MAX_HASHTAGS = 5
    MAX_CONSECUTIVE_CAPS = 10
    
    @classmethod
    def validate(cls, content: str, platform: str = "bluesky") -> Tuple[bool, str]:
        """
        Valida contenuto generato
        
        Args:
            content: Il testo da validare
            platform: Piattaforma target ("bluesky", "linkedin")
        
        Returns:
            Tuple (is_valid: bool, error_message: str)
        """
        
        # 1. Controllo lunghezza
        length_check = cls._check_length(content, platform)
        if not length_check[0]:
            return length_check
        
        # 2. Controllo parole bannate
        banned_check = cls._check_banned_words(content)
        if not banned_check[0]:
            return banned_check
        
        # 3. Controllo pattern sospetti
        pattern_check = cls._check_suspicious_patterns(content)
        if not pattern_check[0]:
            return pattern_check
        
        # 4. Controllo qualità
        quality_check = cls._check_quality(content)
        if not quality_check[0]:
            return quality_check
        
        # 5. Controllo emoji e hashtag
        emoji_check = cls._check_emoji_and_hashtags(content)
        if not emoji_check[0]:
            return emoji_check
        
        logger.info(f"✅ Contenuto validato: {len(content)} caratteri")
        return True, "OK"
    
    @classmethod
    def _check_length(cls, content: str, platform: str) -> Tuple[bool, str]:
        """Controlla lunghezza del contenuto"""
        length = len(content)
        
        if length < cls.MIN_LENGTH:
            return False, f"Contenuto troppo corto: {length} < {cls.MIN_LENGTH} caratteri"
        
        if platform == "bluesky" and length > cls.MAX_LENGTH:
            return False, f"Contenuto troppo lungo per Bluesky: {length} > {cls.MAX_LENGTH}"
        
        return True, "OK"
    
    @classmethod
    def _check_banned_words(cls, content: str) -> Tuple[bool, str]:
        """Controlla presenza di parole bannate"""
        content_lower = content.lower()
        
        for word in cls.BANNED_WORDS:
            if word in content_lower:
                logger.warning(f"Parola bannata trovata: {word}")
                return False, f"Contiene parola bannata: '{word}'"
        
        return True, "OK"
    
    @classmethod
    def _check_suspicious_patterns(cls, content: str) -> Tuple[bool, str]:
        """Controlla pattern sospetti con regex"""
        import re
        
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, content):
                logger.warning(f"Pattern sospetto trovato: {pattern}")
                return False, f"Contiene pattern sospetto: {pattern}"
        
        return True, "OK"
    
    @classmethod
    def _check_quality(cls, content: str) -> Tuple[bool, str]:
        """Controlla qualità generale del contenuto"""
        
        # Troppo maiuscolo consecutivo (SPAM!!!!)
        import re
        caps_sequences = re.findall(r'[A-Z]{2,}', content)
        max_caps = max([len(seq) for seq in caps_sequences]) if caps_sequences else 0
        
        if max_caps > cls.MAX_CONSECUTIVE_CAPS:
            return False, f"Troppo maiuscolo consecutivo: {max_caps} caratteri"
        
        # Controlla se ha senso (almeno alcuni spazi)
        words = content.split()
        if len(words) < 5:
            return False, "Contenuto troppo frammentato"
        
        # Media lunghezza parole (evita gibberish)
        avg_word_length = sum(len(w) for w in words) / len(words)
        if avg_word_length < 2 or avg_word_length > 20:
            return False, f"Lunghezza media parole anomala: {avg_word_length:.1f}"
        
        return True, "OK"
    
    @classmethod
    def _check_emoji_and_hashtags(cls, content: str) -> Tuple[bool, str]:
        """Controlla uso appropriato di emoji e hashtag"""
        
        # Conta emoji (approssimativo - caratteri Unicode alti)
        emoji_count = sum(1 for c in content if ord(c) > 127000)
        if emoji_count > cls.MAX_EMOJI_COUNT:
            return False, f"Troppi emoji: {emoji_count} > {cls.MAX_EMOJI_COUNT}"
        
        # Conta e controlla hashtag
        hashtags = [word for word in content.split() if word.startswith('#')]
        
        if len(hashtags) > cls.MAX_HASHTAGS:
            return False, f"Troppi hashtag: {len(hashtags)} > {cls.MAX_HASHTAGS}"
        
        # Controlla hashtag duplicati
        if len(hashtags) != len(set(hashtags)):
            return False, "Hashtag duplicati trovati"
        
        # Hashtag troppo lunghi
        for tag in hashtags:
            if len(tag) > 30:
                return False, f"Hashtag troppo lungo: {tag}"
        
        return True, "OK"


def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0):
    """
    Decorator per retry con exponential backoff
    
    Args:
        max_retries: Numero massimo di tentativi
        initial_delay: Delay iniziale in secondi
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Tentativo {attempt + 1}/{max_retries} fallito: {e}")
                    
                    if attempt < max_retries - 1:
                        logger.info(f"Retry tra {delay:.1f}s...")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"Tutti i {max_retries} tentativi falliti")
                        raise last_exception
            
        return wrapper
    return decorator


class ContentGenerator:
    """
    Generatore di contenuti social usando Groq AI
    
    Features:
    - Generazione intelligente con Llama 3.3 70B
    - Validazione automatica qualità
    - Retry logic con backoff
    - Template dinamici per varietà
    - Supporto multi-piattaforma
    """
    
    # Modelli disponibili su Groq
    MODELS = {
        'default': 'llama-3.3-70b-versatile',
        'fast': 'llama-3.1-8b-instant',
        'creative': 'llama-3.3-70b-versatile'
    }
    
    def __init__(self, api_key: str, model: str = 'default'):
        """
        Inizializza il generatore
        
        Args:
            api_key: Groq API key
            model: Nome del modello ('default', 'fast', 'creative')
        """
        if not api_key or api_key == "your_groq_key_here":
            raise ValueError("API key Groq non valida")
        
        self.client = Groq(api_key=api_key)
        self.model = self.MODELS.get(model, self.MODELS['default'])
        self.validator = ContentValidator()
        
        logger.info(f"✅ ContentGenerator inizializzato con modello: {self.model}")
        
        # Template di system prompts per varietà
        self.system_prompts = [
            "Sei un esperto di tecnologia che spiega concetti complessi in modo semplice e accessibile. Usi esempi pratici e analogie efficaci.",
            
            "Sei un developer esperto che condivide tips pratici dal mondo tech. Il tuo stile è diretto, tecnico ma chiaro, con focus su applicazioni reali.",
            
            "Sei un tech enthusiast appassionato che educa su AI, machine learning e innovazione. Il tuo tono è entusiasta ma professionale, sempre basato su fatti.",
            
            "Sei un educator tech che rende accessibili argomenti complessi. Usi un approccio step-by-step e non dai mai nulla per scontato.",
            
            "Sei un tech curator che identifica e condivide le tendenze più interessanti. Hai un occhio critico per l'innovazione significativa."
        ]
    
    @retry_with_backoff(max_retries=3, initial_delay=2.0)
    def generate_post(self, 
                      topic: str, 
                      platform: str = "bluesky",
                      style: Optional[str] = None) -> str:
        """
        Genera un post social su un topic specifico
        
        Args:
            topic: L'argomento del post
            platform: "bluesky" o "linkedin"
            style: Stile opzionale ('educational', 'technical', 'conversational')
        
        Returns:
            Il contenuto del post generato e validato
        
        Raises:
            ValueError: Se il contenuto non passa la validazione dopo retry
            Exception: Per errori API
        """
        
        logger.info(f"🤖 Generando post su: '{topic[:60]}...' per {platform}")
        start_time = time.time()
        
        # Configura parametri in base alla piattaforma
        platform_config = self._get_platform_config(platform)
        
        # Costruisci prompt
        user_prompt = self._build_user_prompt(topic, platform_config, style)
        system_prompt = random.choice(self.system_prompts)
        
        try:
            # Chiamata a Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=600,
                top_p=0.9,
                stream=False
            )
            
            content = response.choices[0].message.content.strip()
            generation_time = time.time() - start_time
            
            logger.info(f"⚡ Generato in {generation_time:.2f}s: {len(content)} caratteri")
            
            # Valida il contenuto
            is_valid, error_msg = self.validator.validate(content, platform)
            
            if not is_valid:
                logger.warning(f"⚠️ Validazione fallita: {error_msg}")
                # Tenta di fixare il contenuto
                content = self._fix_content(content, error_msg, platform)
                
                # Ri-valida
                is_valid, error_msg = self.validator.validate(content, platform)
                if not is_valid:
                    raise ValueError(f"Contenuto non valido dopo fix: {error_msg}")
            
            logger.info(f"✅ Post validato e pronto per pubblicazione")
            return content
            
        except Exception as e:
            logger.error(f"❌ Errore generazione: {type(e).__name__}: {e}")
            
            # Se siamo all'ultimo retry, ritorna fallback
            if hasattr(e, '__traceback__'):
                logger.debug("Usando fallback post...")
                return self._fallback_post(topic, platform)
            
            raise
    
    def _get_platform_config(self, platform: str) -> Dict:
        """Ritorna configurazione per la piattaforma"""
        configs = {
            "bluesky": {
                "max_length": "280 caratteri (come Twitter/X)",
                "format_tips": "1-2 emoji strategici, max 3 hashtag, tono conversazionale e autentico",
                "structure": "Hook + Insight + Value proposition + Call to action (opzionale)"
            },
            "linkedin": {
                "max_length": "1200 caratteri (ideale 800-1000)",
                "format_tips": "Hook forte in prima riga, 3-5 bullet points, emoji professionali, 3-5 hashtag",
                "structure": "Hook + Contesto + Insights (bullet points) + Takeaway + CTA"
            }
        }
        
        return configs.get(platform, configs["bluesky"])
    
    def _build_user_prompt(self, topic: str, config: Dict, style: Optional[str]) -> str:
        """Costruisce il prompt per l'AI"""
        
        style_guidance = {
            'educational': "Approccio didattico, spiega il 'perché', usa analogie",
            'technical': "Focus su dettagli tecnici, best practices, esempi di codice (se appropriato)",
            'conversational': "Tono casual e personale, come una conversazione tra colleghi"
        }
        
        style_line = f"\n- Stile: {style_guidance.get(style, 'Scegli lo stile più appropriato')}" if style else ""
        
        return f"""Scrivi un post {config.get('structure', 'strutturato')} su questo topic:

TOPIC: {topic}

REQUISITI TECNICI:
- Lunghezza: {config['max_length']}
- Formato: {config['format_tips']}
- Struttura: {config.get('structure', 'Libera ma coerente')}{style_line}

REQUISITI DI QUALITÀ:
- Deve educare o dare valore reale
- Evita cliché e frasi fatte ("game-changer", "revolutionary", etc.)
- Usa dati o esempi concreti quando possibile
- Sii specifico, non generico
- Tono autentico e professionale
- NO spam, NO click-bait, NO promesse irrealistiche

IMPORTANTE: Scrivi SOLO il testo del post finale, senza spiegazioni o meta-commenti."""
    
    def _fix_content(self, content: str, error_msg: str, platform: str) -> str:
        """
        Tenta di fixare contenuto che non ha passato validazione
        
        Args:
            content: Contenuto originale
            error_msg: Messaggio di errore dalla validazione
            platform: Piattaforma target
        
        Returns:
            Contenuto fixato
        """
        logger.info(f"🔧 Tentativo fix contenuto: {error_msg}")
        
        # Fix troppo lungo
        if "troppo lungo" in error_msg.lower():
            return self._shorten_content(content, platform)
        
        # Fix troppi emoji
        if "emoji" in error_msg.lower():
            # Rimuovi emoji in eccesso
            return self._reduce_emoji(content)
        
        # Fix hashtag
        if "hashtag" in error_msg.lower():
            return self._fix_hashtags(content)
        
        # Fix generico: prova a rimuovere parti problematiche
        return content[:280] if platform == "bluesky" else content
    
    def _shorten_content(self, long_content: str, platform: str) -> str:
        """Accorcia contenuto troppo lungo usando AI"""
        max_length = 280 if platform == "bluesky" else 1000
        
        prompt = f"""Rendi questo post più conciso (max {max_length} caratteri) mantenendo il messaggio principale:

{long_content}

Versione concisa:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            shortened = response.choices[0].message.content.strip()
            logger.info(f"✂️ Accorciato da {len(long_content)} a {len(shortened)} caratteri")
            return shortened
            
        except Exception as e:
            logger.error(f"Errore accorciamento: {e}")
            # Fallback: tronca manualmente
            return long_content[:max_length-3] + "..."
    
    def _reduce_emoji(self, content: str) -> str:
        """Riduce numero di emoji nel contenuto"""
        # Identifica emoji (caratteri Unicode alti)
        emoji_chars = [c for c in content if ord(c) > 127000]
        
        if len(emoji_chars) <= 5:
            return content
        
        # Rimuovi emoji in eccesso (mantieni i primi 3)
        result = content
        for emoji in emoji_chars[3:]:
            result = result.replace(emoji, '', 1)
        
        logger.info(f"✂️ Rimossi {len(emoji_chars) - 3} emoji in eccesso")
        return result
    
    def _fix_hashtags(self, content: str) -> str:
        """Fix problemi con hashtag"""
        words = content.split()
        hashtags = [w for w in words if w.startswith('#')]
        
        # Rimuovi duplicati
        unique_hashtags = []
        seen = set()
        for tag in hashtags:
            if tag.lower() not in seen:
                unique_hashtags.append(tag)
                seen.add(tag.lower())
        
        # Limita a 3 hashtag
        if len(unique_hashtags) > 3:
            unique_hashtags = unique_hashtags[:3]
        
        # Ricostruisci contenuto
        result = content
        for old_tag in hashtags:
            if old_tag not in unique_hashtags:
                result = result.replace(old_tag, '', 1)
        
        return result.strip()
    
    def _fallback_post(self, topic: str, platform: str) -> str:
        """
        Post di emergenza se tutto fallisce
        
        Ritorna un post sicuro e generico
        """
        logger.warning("⚠️ Usando fallback post - generazione fallita")
        
        templates = [
            f"💡 Oggi esploro: {topic}\n\nInsights e riflessioni in arrivo!\n\n#Tech #AI",
            f"🔍 Deep dive su: {topic}\n\nCosa ne pensate? Condividete la vostra esperienza.\n\n#Development",
            f"🚀 Nuovo topic: {topic}\n\nRisorse e best practices coming soon.\n\n#TechCommunity"
        ]
        
        return random.choice(templates)
    
    def generate_multiple_variants(self, topic: str, count: int = 3, platform: str = "bluesky") -> List[str]:
        """
        Genera multiple varianti di un post per lo stesso topic
        
        Args:
            topic: Topic del post
            count: Numero di varianti da generare
            platform: Piattaforma target
        
        Returns:
            Lista di varianti del post
        """
        logger.info(f"🎨 Generando {count} varianti per: {topic}")
        
        variants = []
        styles = ['educational', 'technical', 'conversational']
        
        for i in range(count):
            try:
                style = styles[i % len(styles)]
                variant = self.generate_post(topic, platform, style)
                variants.append(variant)
                
                # Pausa per evitare rate limiting
                if i < count - 1:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Errore generazione variante {i+1}: {e}")
                continue
        
        logger.info(f"✅ Generate {len(variants)}/{count} varianti")
        return variants


# Funzione helper per uso standalone
def quick_generate(topic: str, api_key: str, platform: str = "bluesky") -> str:
    """
    Helper function per generazione rapida
    
    Args:
        topic: Topic del post
        api_key: Groq API key
        platform: Piattaforma target
    
    Returns:
        Post generato
    """
    generator = ContentGenerator(api_key)
    return generator.generate_post(topic, platform)


if __name__ == "__main__":
    # Test standalone
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY non trovata in .env")
        exit(1)
    
    print("🧪 Test ContentGenerator\n")
    
    # Test generazione
    generator = ContentGenerator(api_key)
    
    test_topic = "Come l'AI sta trasformando lo sviluppo software"
    print(f"📝 Generando post su: {test_topic}\n")
    
    try:
        post = generator.generate_post(test_topic, platform="bluesky")
        print("="*60)
        print("POST GENERATO:")
        print("="*60)
        print(post)
        print("="*60)
        print(f"\n✅ Lunghezza: {len(post)} caratteri")
        
        # Test validazione
        is_valid, msg = ContentValidator.validate(post, "bluesky")
        print(f"✅ Validazione: {msg}")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
