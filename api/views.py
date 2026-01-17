from django.shortcuts import render
from django.contrib.auth import get_user_model
from .serializers import DocumentSerializer, DocumentListSerializer
from .models import Document
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


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

            return Response({
                'id': document.id,
                'title': document.title,
                'status': document.status,
                'message': 'Document uploaded successfully'
            }, status=status.HTTP_201_CREATED)
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
    



