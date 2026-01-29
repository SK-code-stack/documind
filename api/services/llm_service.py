from google import genai
from django.conf import settings
from decouple import config


class LLMService:
    """Service for interacting with Google Gemini API"""
    
    # Model configuration
    MODEL_NAME = 'gemini-2.5-flash'
    _client = None
    
    @classmethod
    def get_client(cls):
        """
        Initialize and return Gemini client
        
        Returns:
            genai: Configured Gemini client
        """
        if cls._client is None:
            api_key = config('GEMINI_API_KEY', default=None)
            
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            cls._client = genai.Client(api_key=api_key)
            print("Gemini API client initialized successfully!")
        
        return cls._client
    
    @staticmethod
    def generate_answer(prompt):
        """
        Generate answer using Gemini API
        
        Args:
            prompt: Formatted prompt with context and question
        
        Returns:
            str: Generated answer
        """
        client = LLMService.get_client()
        
        try:
            print("Sending request to Gemini API...")
            
            # Use the correct Gemini API syntax
            response = client.models.generate_content(
                model=LLMService.MODEL_NAME,
                contents=prompt
            )
            
            # Extract text from response
            answer = response.text
            
            print(f"Received answer ({len(answer)} characters)")
            return answer
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            raise ValueError(f"Failed to generate answer: {str(e)}")
    
    @staticmethod
    def count_tokens(text):
        """
        Count tokens in text (approximate)
        
        Args:
            text: Text to count tokens for
        
        Returns:
            int: Token count (approximate)
        """
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4