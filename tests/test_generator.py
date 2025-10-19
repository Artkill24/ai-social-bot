import unittest
from unittest.mock import Mock, patch
from src.content.generator import ContentGenerator, ContentValidator

class TestContentGenerator(unittest.TestCase):
    
    def setUp(self):
        self.generator = ContentGenerator("test_api_key")
    
    def test_content_validator_min_length(self):
        """Test validazione lunghezza minima"""
        short_content = "Too short"
        is_valid, msg = ContentValidator.validate(short_content)
        self.assertFalse(is_valid)
        self.assertIn("Contenuto troppo corto", msg)
    
    def test_content_validator_banned_words(self):
        """Test filtro parole bannate"""
        spam_content = "Check out this spam offer!" * 10
        is_valid, msg = ContentValidator.validate(spam_content)
        self.assertFalse(is_valid)
        self.assertIn("bannata", msg)
    
    @patch('src.content.generator.Groq')
    def test_generate_post_success(self, mock_groq):
        """Test generazione post con successo"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test post content"))]
        mock_groq.return_value.chat.completions.create.return_value = mock_response
        
        content = self.generator.generate_post("AI Testing")
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 0)

if __name__ == '__main__':
    unittest.main()
