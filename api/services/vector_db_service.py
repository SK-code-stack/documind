import chromadb
from chromadb.config import settings
import os
from django.conf import settings as django_settings

class vector_db_service:
    """
    Service for managing vector database operations with chromaDB
    """

    # ChromaDB client (singleton)
    _client = None

    # Database path
    CHROMA_DB_PATH = os.path.join(django_settings.BASE_DIR, 'chromadb_data')

    
    @classmethod
    def get_client(cls):
        """
        Get or create chroma db client
        Return:
            chromadb.client : chromaDB client instance
        """
        if cls._client is None:
            # Create directory if it does not exists
            os.mkdir(cls.CHROMA_DB_PATH, exist_ok=True)

            print(f"Initializing ChromaDB at: {cls.CHROMA_DB_PATH}")

            #  Initialize client with persistent storage
            cls._client = chromadb.PersistentClient(
                path=cls.CHROMA_DB_PATH,
                settings=settings(
                    anonymized_telemetry = False,
                    allow_reset = True
                )
            )
            print(f"ChromaDB initialized successfully!")
        return cls._client
