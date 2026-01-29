from .search_service import SearchService
from .llm_service import LLMService
from ..prompts.chat_prompts import get_chat_prompt, get_system_instruction
from ..models import Document, ChatMessage


class ChatService:
    """Service for handling document chat"""
    
    @staticmethod
    def ask_question(document_id, user, question, top_k=5):
        """
        Ask a question about a document
        
        Args:
            document_id: Document ID
            user: User instance
            question: User's question
            top_k: Number of chunks to retrieve
        
        Returns:
            dict: Answer with sources
        """
        # Validate document
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            raise ValueError(f"Document with id {document_id} not found")
        
        if document.user != user:
            raise ValueError("You don't have access to this document")
        
        if document.status != 'completed':
            raise ValueError(f"Document is not ready. Status: {document.status}")
        
        # Step 1: Search for relevant chunks
        print(f"Searching document for: '{question}'")
        search_results = SearchService.search_document(
            document_id=document_id,
            query=question,
            top_k=top_k
        )
        
        if not search_results['chunks']:
            return {
                'answer': "I couldn't find any relevant information in the document to answer this question.",
                'sources': [],
                'question': question
            }
        
        # Step 2: Build context from search results
        context = SearchService.build_context(search_results, max_token=2000)
        
        # Step 3: Create prompt
        prompt = get_chat_prompt(
            query=question,
            context=context,
            document_title=document.title
        )
        
        # Step 4: Generate answer using Gemini
        print("Generating answer with Gemini...")
        answer = LLMService.generate_answer(prompt)
        
        # Step 5: Get source references
        sources = SearchService.get_source_references(search_results)
        
        # Step 6: Save to chat history
        # Save user question
        ChatMessage.objects.create(
            document=document,
            user=user,
            role='user',
            content=question
        )
        
        # Save AI answer with sources
        source_ids = [s['chunk_id'] for s in sources]
        ChatMessage.objects.create(
            document=document,
            user=user,
            role='assistant',
            content=answer,
            sources=source_ids
        )
        
        print(f"Chat saved to history")
        
        # Return response
        return {
            'answer': answer,
            'sources': sources,
            'question': question,
            'chunks_used': len(sources)
        }
    
    @staticmethod
    def get_chat_history(document_id, user, limit=50):
        """
        Get chat history for a document
        
        Args:
            document_id: Document ID
            user: User instance
            limit: Maximum messages to return
        
        Returns:
            list: Chat messages
        """
        # Validate access
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            raise ValueError(f"Document with id {document_id} not found")
        
        if document.user != user:
            raise ValueError("You don't have access to this document")
        
        # Get messages
        messages = ChatMessage.objects.filter(
            document=document,
            user=user
        ).order_by('created_at')[:limit]
        
        return messages
    
    @staticmethod
    def clear_chat_history(document_id, user):
        """
        Clear chat history for a document
        
        Args:
            document_id: Document ID
            user: User instance
        
        Returns:
            int: Number of messages deleted
        """
        # Validate access
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            raise ValueError(f"Document with id {document_id} not found")
        
        if document.user != user:
            raise ValueError("You don't have access to this document")
        
        # Delete messages
        count, _ = ChatMessage.objects.filter(
            document=document,
            user=user
        ).delete()
        
        print(f"Deleted {count} messages")
        return count