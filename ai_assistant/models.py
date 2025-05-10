# ai_assistant/models.py

from django.db import models
from django.contrib.auth.models import User
from boards.models import Board, Card

class AIPromptTemplate(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    prompt_text = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class AIAssistantInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=True, blank=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True, blank=True)
    prompt = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'AI Interaction by {self.user.username} at {self.created_at}'

class AICardSuggestion(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    suggested_list = models.CharField(max_length=200, blank=True)
    priority = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_applied = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'AI Suggestion: {self.title}'