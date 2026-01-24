from sentence_transformers import SentenceTransformer
import numpy as np
from ..models import DocumentChunk

class EmbeddingService:
    """Servide for generating embeddings of text"""

    # Model
    MODEL_NAME = 'all-MiniLM-L6-v2' 
    _model = None

    @classmethod
    def get_model(cls):
        """
        Load and cache the embedding model
        
        Return:
            sentence transformer load model
        """
        if cls._model is None:
            print(f"Loading embedding model : {cls.MODEL_NAME} ... ")
            cls._model = SentenceTransformer(cls.MODEL_NAME)
            print("Model load successfully! ")
        return cls._model
    
    @staticmethod
    def generate_embedding(text):
        """
        Generate embeddings for single text 
        Args: 
            text : text to embed
        """
