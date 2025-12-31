from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.

class Document(models.Model):

    status_choice = [
        ('pending', 'pending'),
        ('processing', 'processing'),
        ('completed', 'completed'),
        ('failed', 'failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/%y/%m/%d')
    file_size = models.IntegerField(help_text='File size in bytes')
    page_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=status_choice, default='pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    process_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)


    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['uploaded_at'])
        ]

    def __str__(self):
        return f'{self.title} - {self.user.email}'
    
    def mark_as_processing(self):
        self.status = 'processing'
        self.save()

    def mark_as_completed(self):
        self.status = 'completed'
        self.process_at = timezone.now()
        self.save()


    def mark_as_failed(self, error):
        self.status = 'failed'
        self.error_message = error
        self.save()

        

class DocumentChunk(models.Model):

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    chunk_index = models.IntegerField()
    page_number = models.IntegerField(null=True, blank=True)
    embedding = models.JSONField(null=True, blank=True) # store data as json array 
    token_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]
        unique_together = ['document', 'chunk_index']

    def __str__(self):
        return f'{self.chunk_index} - {self.document.title}'
    

class ChatMessage(models.Model):
    
    ROLE_CHOICES = [
        ('user','User'),
        ('assistant','Assistant'),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name='chat_messages')
    role = models.CharField(choices=ROLE_CHOICES, max_length=20)
    content = models.TextField()
    sources = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['document', 'created_at']),
        ]

    def __str__(self):
        return f'{self.role} - {self.content[:50]} ...'