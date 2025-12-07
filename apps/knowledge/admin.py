from django.contrib import admin
from .models import Knowledge, Message

class KnowledgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'created_at', 'updated_at']
    list_filter = ['user', 'created_at', 'updated_at']
    search_fields = ['user', 'title']
    ordering = ['-created_at']

admin.site.register(Knowledge, KnowledgeAdmin)

class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'author', 'created_at', 'updated_at']
    list_filter = ['user', 'author', 'created_at', 'updated_at']
    search_fields = ['user', 'content']
    ordering = ['-created_at']

admin.site.register(Message, MessageAdmin)