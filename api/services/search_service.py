from .embedding_service import EmbeddingService
from .vector_db_service import VectorDBService
from ..models import Document, DocumentChunk

class SearchService:
    """
    Service for similarity search in documents
    """

    @staticmethod
    def search_document(document_id, query, top_k=5):
        """
        Docstring for search_document
        
        :param document_id: Document ID
        :param query: User question
        :param top_k: Number of returns to return

        Return:
            dict : search reasult with chunks and metadata
        """
        # Validate document exists and is ready
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            raise ValueError(f"Document with id : {document_id} did not found")

        if document.status != 'completed':
            raise ValueError(f"Document is not ready : {document.status}")
        
        # 1 convert query to embedding
        print(f"Converting query to emeddings ... ")
        query_embedding = EmbeddingService.generate_embedding(query)

        # 2 Search in vector database
        print(f"Searching in vector database ... ")
        results = VectorDBService.search_similar_chunks(
            # perameters to this function
            document_id=document_id,
            query_embedding=query_embedding,
            top_k=top_k,
        )

        # 3 Enrich results with full chunk data from database
        enriched_results = []
        for result in results:
            try:
                chunk = DocumentChunk.objects.get(id=result['chunk_id'])
                enriched_results.append({
                    'chunk_id' : chunk.id,
                    'chunk_index' : chunk.chunk_index,
                    'page_number' : chunk.page_number,
                    'content' : chunk.content,
                    'token_count' : chunk.token_count,
                    'similarity_score' : round(result['similarity_score'], 4),
                })
            except Document.DoesNotExist:
                print(f"Warning: Chunk {result['chunk_id']} not found in database")
                continue
        print(f'Found {len(enriched_results)} relevent chunks')

        return {
            'document_id' : document_id,
            'document_title' : document.title,
            'query' : query,
            'results_count' : len(enriched_results),
            'chunks' : enriched_results,
        }
    

    @staticmethod
    def build_context(search_results, max_token=2000):
        """
         build_context string from search results for llm
        
        :param search_results: Results from search_document()
        :param max_token: Maximum tokens fro context

        Return:
            str : Formatted context for LLM
        """

        context_part = []
        current_tokens = 0

        for i, chunk in enumerate(search_results['chunks'], 1):
            # Check if adding this chunk exceeds token limit
            if  current_tokens + chunk['token_count'] > max_token:
                print(f"Reached token limit. Using {i-1} chunks out of {len(search_results['chunks'])}")
                break

            # add chunk to context
            chunk_header = f"\n\n--- Source {i} (page {chunk['page_number']}, Similarity : {chunk['similarity_score']}) ---\n"
            context_part.append(chunk_header + chunk['content'])
            current_tokens += chunk['token_count']

        context = "\n".join(context_part)
        print(f"Built context with {len(context_part)} chunks, ~{current_tokens}, tokens") 

        return context
    
    @staticmethod
    def get_source_references(search_results):
        """
        Extract source reference from search results
        
        :param search_results: Result from search_document()
        Return:
            list : Source references with page numbers and similarity scores
        """
        sources = []
        for chunk in search_results['chunks']:
            sources.append({
                'chunk_id': chunk['chunk_id'],
                'page_number': chunk['page_number'],
                'similarity_score': chunk['similarity_score'],
                'preview': chunk['content'][:100] + '...' if len(chunk['content']) > 100 else chunk['content']
            })

        return sources
    
