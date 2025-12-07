from rest_framework import serializers
from .models import Knowledge, Message


class KnowledgeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Knowledge
        fields = ['id', 'user', 'title', 'created_at', 'updated_at'] 
        read_only_fields = ['user', 'updated_at']


class KnowledgeUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if value.content_type not in ['application/pdf', 'application/x-pdf']:
            raise serializers.ValidationError('Envie um arquivo PDF válido.')
        if value.size == 0:
            raise serializers.ValidationError('Arquivo vazio.')
        return value


class MessageSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'user', 'content', 'author', 'created_at', 'updated_at'] 