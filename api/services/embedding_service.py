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
        Generate embeddings for single text (use when we convert user question to vector)
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
        texts = [chunk.content for chunk in chunks]

        # Generate embeddings in batch 
        print(f"Generating embeddings for {len(texts)} chunks ... ")
        embeddings = EmbeddingService.generate_embeddings_batch(texts)

        # Update chunks with embeddings
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
            chunk.save()
        
        print(f"Successfully embedded {len(chunks)} chunks!")
        return len(chunks)
    

    @staticmethod
    def get_embedding_dimension():
        """
        Get the dimension of embeddings
        Return:
            int : Embedding dimension
        """

        model = EmbeddingService.get_model()
        return model.get_sentence_embedding_dimension()
    

    @staticmethod
    def calculate_similarity(embedding1, embedding2):
        """
        Calculate cosin similarity of two embeddings
        Args:
            embedding1 : First embedding vector
            embedding2 : Second embedding vector
        Return:
            float : similarity score (0 to 1)
        """

        # Convert to numpy array
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Calculate cosin similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        similarity = dot_product / (norm1 * norm2)
        
        return float(similarity)