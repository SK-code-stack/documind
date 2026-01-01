from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Document, ChatMessage, DocumentChunk

User = get_user_model()

class DocumentChunkSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DocumentChunk
        fields = ['id', 'content', 'chunk_index', 'page_number', 'token_count', 'created_at']
        read_only = ['id', 'created_at']


# Upload file serializer
class DocumentSerializer(serializers.ModelSerializer):

    chunk_count = serializers.SerializerMethodField()
    is_ready = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file', 'file_size', 'page_count', 
            'status', 'uploaded_at', 'processed_at', 'error_message',
            'chunk_count', 'is_ready', 'user_email'
        ]
        read_only_fields = [
            'id', 'file_size', 'page_count', 'status', 
            'uploaded_at', 'processed_at', 'error_message',
            'chunk_count', 'is_ready', 'user_email'
        ]

    def get_chunk_count(self, obj):
        return obj.chunks.count()

    def get_is_ready(self, obj):
        return obj.status == 'completed'

    def validate_file(self, file):
        if not file.name.lower().endswith('.pdf'):
            raise serializers.ValidationError('Only PDF files are allowed')
        
        max_size = 10 * 1024 * 1024
        if file.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        return file 
    
    def create(self, validated_data):
        user = self.context['request'].user
        # extract file name fot title and removing .pdf
        file = validated_data['file']
        title = file.name.rsplit('.',1)[0]

        #saving document 
        document = Document.objects.create(
            user = user,
            title = title,
            file = file,
            file_size = file.size,
            status = 'pending'
        )
        return document
    

class DocumentListSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()
    is_ready = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'status', 'page_count', 
            'uploaded_at', 'chunk_count', 'is_ready'
        ]
        read_only_fields = fields

    

    def get_chunk_count(self, obj):
        return obj.chunks.count()

    def get_is_ready(self, obj):
        return obj.status == 'completed'
    
class ChatMessageSerializer(serializers.ModelSerializer):
    source_chunks = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at', 'source_chunks']
        read_only_fields = ['id', 'created_at', 'source_chunks']

    def get_source_chunks(self, obj):
        if not obj.sources:
            return []
        
        # Get chunk id from source
        chunk_ids = obj.sources
        chunks = DocumentChunk.objects.filter(id__in=chunk_ids)

        # Return simplified chunk information
        return [
            {
                'chunk_index': chunk.chunk_index,
                'page_number': chunk.page_number,
                'content_preview': chunk.content[:100] + '...' if len(chunk.content) > 100 else chunk.content
            }
            for chunk in chunks
        ]


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat question input"""
    
    document_id = serializers.IntegerField()
    question = serializers.CharField(max_length=1000)
    
    def validate_document_id(self, value):
        """Validate document exists and belongs to user"""
        user = self.context['request'].user
        
        try:
            document = Document.objects.get(id=value)
        except Document.DoesNotExist:
            raise serializers.ValidationError("Document not found")
        
        # Check ownership
        if document.user != user:
            raise serializers.ValidationError("You don't have access to this document")
        
        # Check if ready
        if document.status != 'completed':
            raise serializers.ValidationError(f"Document is not ready. Status: {document.status}")
        
        return value
    
    def validate_question(self, value):
        """Validate question is not empty"""
        value = value.strip()
        
        if not value:
            raise serializers.ValidationError("Question cannot be empty")
        
        if len(value) < 3:
            raise serializers.ValidationError("Question too short (min 3 characters)")
        
        return value


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response output"""
    
    answer = serializers.CharField()
    sources = serializers.ListField(
        child=serializers.DictField()
    )
    timestamp = serializers.DateTimeField()
