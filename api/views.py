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


    # list all files of current user 
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).order_by('-uploaded_at')
    
    # user different serializers for differrnt actions
    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer


    @action(detail=False, methods=['post'])
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
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
    
