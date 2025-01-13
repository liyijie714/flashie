from django.db import models
from django.contrib.auth.models import User

class AIModel(models.Model):
    MODEL_TYPES = [
        ('openai', 'OpenAI'),
        ('claude', 'Claude'),
    ]
    
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    is_active = models.BooleanField(default=True)
    api_key_required = models.BooleanField(default=False)
    system_prompt = models.TextField(blank=True)

    def __str__(self):
        return self.display_name

class Role(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role_name = models.CharField(max_length=100)
    role_description = models.TextField()
    greeting = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.role_name

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Chat histories"
