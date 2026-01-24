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
        Return:
            list : embedding vectors
        """
        model = EmbeddingService.get_model()
        
        # Generate embeddings
        embeddings = model.encode(text, convert_to_numpy=True)

        # Convert to json list and return
        return embeddings.tolist()
    

    @staticmethod
    def generate_embeddings_batch(texts):
        """
        Generate embeddings of multiple text at once
        Args:
            text : list of text
        Return:
            list : list of embedding vectors
        """

        model = EmbeddingService.get_model()
        
        # Generate embeddings of multiple text at once
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

        return [emb.tolist() for emb in embeddings]
    

    @staticmethod
    def embed_document_chunks(document):
        """
        Generate embeddings of all chunks of document
        Args:
            document : Document instance
        Return:
            int : Number of chunk embended        
        """
        # Get all chunks without embeddings
        chunks = document.chunks.all()

        if not chunks.exists():
            raise ValueError("No chunk found for this document")
        
        # Find exact chunk from the document
        text = [chunk.content for chunk in chunks]

        # Generate embeddings in batch 
        print(f"Generating embeddings for {len(text)} chunks ... ")
        embeddings = EmbeddingService.generate_embeddings_batch(texts)

        # Update chunks with embeddings
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
            chunk.save()
        
        print(f"Successfully embedded {len(chunks)} chunks!")
        return len(chunks)