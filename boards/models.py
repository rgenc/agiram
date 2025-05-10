# boards/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Board(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(User, related_name='member_boards', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('boards:board_detail', kwargs={'pk': self.pk})

class List(models.Model):
    title = models.CharField(max_length=200)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='lists')
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return self.title

class Card(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='cards')
    assigned_to = models.ManyToManyField(User, related_name='assigned_cards', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_cards')
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        return self.due_date and not self.is_completed and self.due_date < timezone.now()

class Comment(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.card.title}'

class Attachment(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Attachment on {self.card.title}'

class Activity(models.Model):
    ACTION_CHOICES = [
        ('create_card', 'Kart Oluşturuldu'),
        ('move_card', 'Kart Taşındı'),
        ('assign_card', 'Kart Atandı'),
        ('comment_card', 'Yorum Yapıldı'),
        ('complete_card', 'Kart Tamamlandı'),
        ('reopen_card', 'Kart Yeniden Açıldı'),
    ]
    
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True, blank=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activities'
    
    def __str__(self):
        return f'{self.user.username} {self.get_action_display()}'