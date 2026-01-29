from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
# Models
from .models import Document
# Serializers
from .serializers import (
    DocumentSerializer, DocumentListSerializer, 
    ChatRequestSerializer, ChatResponseSerializer, ChatHistorySerializer
)
# Services
from .services.pdf_service import PDFservice
from .services.chunking_service import ChunkingService
from .services.embedding_service import EmbeddingService
from .services.vector_db_service import VectorDBService
from .services.search_service import SearchService
from .services.llm_service import LLMService



# Create your views here.

User = get_user_model()


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]


    # list all files of current user api/document
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).order_by('-uploaded_at')
    
    # user different serializers for differrnt actions 
    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer

    # Upload file to the server
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def upload(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error':'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DocumentSerializer(data=request.data, context={'request':request})

        if serializer.is_valid():
            document = serializer.save()

            # Mark as processing
            document.mark_as_processing()
            
            try:
                # extract text from pdf
                print("Extracting text from pdf ...")
                pdf_data = PDFservice.extract_text_from_pdf(document.file.path)

                # Chunk the text
                print("Chunking text ...")
                chunk_count = ChunkingService.chunk_deocument(document, pdf_data)

                # Generating embeddings
                print("Generating embeddings ...")
                embedded_count = EmbeddingService.embed_document_chunks(document)

                # Add to vector database
                print("Adding to vector database ...")
                VectorDBService.add_chunks_to_collection(document.id, document.chunks.all())

                # Update document
                document.page_count = pdf_data['page_count']
                document.mark_as_completed()

                print("Processing complete!")

                return Response({
                    'id': document.id,
                    'title': document.title,
                    'status': document.status,
                    'page_count': document.page_count,
                    'chunk_count':chunk_count,
                    'embedded_chunks': embedded_count,
                    'message': 'Document uploaded and processed successfully successfully',

                }, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                # Mark as failed if process failed
                import traceback
                error_detail = traceback.format_exc()
                print (f"Error : {error_detail}")
                document.mark_as_failed(str(e))

                return Response({
                    'id': document.id,
                    'title': document.title,
                    'status': 'failed',
                    'error': str(e),
                    'message': 'Document uploaded but process failed'
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    # Delete the selected document
    def destroy(self, request, pk=None):
        document = self.get_object()
        
        if document.file:
            document.file.delete()
        
        document.delete()

        return Response({
            'message': 'Document deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    
    # Get document process status
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        document = self.get_object()

        return Response(
            {
            'id': document.id,
            'status': document.status,
            'error_message': document.error_message,
            'page_count': document.page_count,
            'chunk_count': document.chunks.count(),
            'is_ready': document.status == 'completed'
            }
        )
    


    @action(detail=True, methods=['post'])
    def search(self, request, pk=None):
        """
        Search for relevent chunk from the document
        
        : Request body:
        {
            "query": "What is the user's experience?",
            "top_k": 5  (optional, default: 5)
        }
        """

        document = self.get_object()
        query = request.data.get('query')
        top_k = request.data.get('top_k', 5)

        if not query:
            return Response({'error':'Query is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Search document 
            document_chunks = SearchService.search_document(
                document_id=document.id,
                query=query,
                top_k=top_k
            )
            # Context for ai 
            context = SearchService.build_context(document_chunks)

            # Responce from ai
            results = GeminiService.ask_ai(query, context)

            return Response(f"Ai response : {results}", status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({'error': f'Search failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        """
        Ask a question about the document
        
        Request body:
        {
            "question": "What is the user's experience?",
            "top_k": 5  (optional)
        }
        """
        from .services.chat_service import ChatService
        
        document = self.get_object()
        
        # Validate request
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question = serializer.validated_data['question']
        top_k = serializer.validated_data.get('top_k', 5)
        
        try:
            # Ask question
            result = ChatService.ask_question(
                document_id=document.id,
                user=request.user,
                question=question,
                top_k=top_k
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response(
                {'error': f'Chat failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def chat_history(self, request, pk=None):
        """Get chat history for document"""
        from .services.chat_service import ChatService
        
        document = self.get_object()
        
        try:
            messages = ChatService.get_chat_history(
                document_id=document.id,
                user=request.user
            )
            
            serializer = ChatHistorySerializer(messages, many=True)
            
            return Response({
                'document_id': document.id,
                'message_count': len(messages),
                'messages': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def clear_history(self, request, pk=None):
        """Clear chat history for document"""
        from .services.chat_service import ChatService
        
        document = self.get_object()
        
        try:
            count = ChatService.clear_chat_history(
                document_id=document.id,
                user=request.user
            )
            
            return Response({
                'message': f'Cleared {count} messages',
                'deleted_count': count
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# http://127.0.0.1:8000/api/documents/upload/