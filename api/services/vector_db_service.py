import chromadb
from chromadb.config import Settings
import os
from django.conf import settings as django_settings

class VectorDBService:
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
            os.makedirs(cls.CHROMA_DB_PATH, exist_ok=True)

            print(f"Initializing ChromaDB at: {cls.CHROMA_DB_PATH}")

            #  Initialize client with persistent storage
            cls._client = chromadb.PersistentClient(
                path=cls.CHROMA_DB_PATH,
                settings=Settings(
                    anonymized_telemetry = False,
                    allow_reset = True
                )
            )
            print(f"ChromaDB initialized successfully!")
        return cls._client
    
    @ staticmethod
    def get_collection_name(document_id):
        """
        Generate collection name for the document 
        Args:
            document_id : Document ID
        Returns:
            str : Collection name
        """
        return f"document_{document_id}"
    
    @staticmethod
    def create_collection(document_id):
        """
        Create collection for the document
        Args:
            document_id : Document ID
        return:
            chromadb.Collection : Create Collection
        """

        client = VectorDBService.get_client()
        collection_name = VectorDBService.get_collection_name(document_id)

        # Delete exixting collection if any exists
        try:
            client.delete_collection(name = collection_name)
            print(f"Deleted existing collection : {collection_name}")
        except:
            pass

        # Create new collection
        collection = client.create_collection(
            name = collection_name,
            metadata = {'document_id':document_id}
        )

        print(f"Created collection : {collection_name}")
        return collection
    
    @staticmethod
    def add_chunks_to_collection(document_id, chunks):
        """
        Docstring for add_chunks_to_collection
        
        :param document_id: Document ID
        :param chunks: Queryset or list of DocumentChunk objects

        return:
            int : Number of chunk added
        """
        # Create collection
        collection = VectorDBService.create_collection(document_id)

        # Prepare data
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in chunks:
            ids.append(f"chunk : {chunk.id}")
            embeddings.append(chunk.embedding)
            documents.append(chunk.content)
            metadatas.append(
                {
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number or 0,
                "token_count": chunk.token_count
                }
            )

            # Add to collection in batch
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )

        print(f"Added {len(ids)} chunks to ChromaDB collection")
        return len(ids)


    @staticmethod
    def search_similar_chunks(document_id, query_embedding, top_k=5):
        """
        Docstring for search_similar_chunks
        
        :param document_id: Document ID
        :param query_embedding: Query embedding vector
        :param top_k: Number of results to return

        Return: 
            dict : search results with chunks and store
        """
        client = VectorDBService.get_client()
        collection_name = VectorDBService.get_collection_name(document_id)

        try:
            collection = client.get_collection(name=collection_name)
        except:
            raise ValueError(f"Collection not found : {document_id}")

        # Search for similar vector
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        formatted_result = []
        for i in range(len(results['ids'][0])):

            # Convert to similarity score (0-1 range)
            distance = results['distances'][0][i]
        
            # Lower distance = higher similarity
            similarity_score = 1 / (1 + distance)  # ✅ Always between 0 and 1

            formatted_result.append({
                'chunk_id': results['metadatas'][0][i]['chunk_id'],
                'chunk_index': results['metadatas'][0][i]['chunk_index'],
                'page_number': results['metadatas'][0][i]['page_number'],
                'content': results['documents'][0][i],
                'similarity_score': similarity_score # Convert distance to similarity
            })

        return formatted_result
    
    @staticmethod
    def delete_collection(document_id):
        """
        Docstring for delete_collection
        
        :param document_id: Document ID
        """
        client = VectorDBService.get_client()
        collection_name = VectorDBService.get_collection_name(document_id)

        try:
            client.delete_collection(name=collection_name)
            print(f"Deleted collection : {collection_name}")
        except:
            print(f"Collection did not found or already deleted : {collection_name}")

    @staticmethod
    def get_collection_stats(document_id):
        """
        Docstring for get_collection_stats
        
        :param document_id: Document ID

        Returns:
            dict : Collection statistics
        """
        client = VectorDBService.get_client()
        collection_name = VectorDBService.get_collection_name(document_id)

        try:
            collection = client.get_collection(name=collection_name)
            count = collection.count()
            
            return {
                'collection_name': collection_name,
                'document_id': document_id,
                'total_vectors': count,
                'exists': True
            }
        except:
            return {
                'collection_name': collection_name,
                'document_id': document_id,
                'total_vectors': 0,
                'exists': False
            }
        