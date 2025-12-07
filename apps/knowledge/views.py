from pathlib import Path

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from .models import Knowledge, Message
from .serializers import KnowledgeSerializer, KnowledgeUploadSerializer, MessageSerializer
from .tasks import ingest_pdf_and_create_knowledge
from .rag_service import RAG_Service 


class KnowledgeViewSet(viewsets.ModelViewSet):
    serializer_class = KnowledgeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        #Retorna apenas os conhecimentos do usuário autenticado
        return Knowledge.objects.filter(
            user=self.request.user,
            is_deleted=False
        )

    def create(self, request, *args, **kwargs):
        # Bloqueio 
        return Response(
            {"detail": "Use /api/knowledge/upload/ para enviar o PDF e criar o conhecimento após ingestão."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def perform_create(self, serializer):
        #Associa automaticamente o usuário ao criar um conhecimento
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='upload', permission_classes=[IsAuthenticated])
    def upload(self, request):
        """
        Recebe um PDF, salva no disco e dispara a task de ingestão via Celery.
        O Knowledge só é criado após a ingestão ser concluída pela task.
        """
        serializer = KnowledgeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']
        title = serializer.validated_data.get('title') or Path(uploaded_file.name).stem

        upload_dir = Path(settings.MEDIA_ROOT) / 'knowledge_uploads'
        upload_dir.mkdir(parents=True, exist_ok=True)

        storage = FileSystemStorage(location=upload_dir)
        saved_name = storage.save(uploaded_file.name, uploaded_file)
        file_path = storage.path(saved_name)

        task = ingest_pdf_and_create_knowledge.delay(
            user_id=request.user.id,
            title=title,
            file_path=file_path,
        )

        return Response(
            {
                "detail": "Ingestão iniciada"
            },
            status=status.HTTP_202_ACCEPTED,
        )

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        #Retorna apenas as mensagens do usuário autenticado
        return Message.objects.filter(
            user=self.request.user,
        )
    

    def create(self, request, *args, **kwargs):
        """Cria mensagem do usuário, consulta RAG e cria mensagem de resposta do sistema."""

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_message = serializer.save(
            user=request.user,
            author='user'
        )
        
        try:
            rag_response = RAG_Service.answer_question(
                question=user_message.content,
                user_id=str(request.user.id)
            )
            
            system_message = Message.objects.create(
                user=request.user,
                content=rag_response,
                author='system'
            )
            
            system_serializer = MessageSerializer(system_message)
            
            return Response(
                {
                    "system_message": system_serializer.data,
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            # Se houver erro no RAG, ainda retorna a mensagem do usuário criada
            # mas adiciona informação do erro
            user_serializer = MessageSerializer(user_message)
            return Response(
                {
                    "user_message": user_serializer.data,
                    "system_message": None,
                    "error": f"Erro ao consultar RAG: {str(e)}"
                },
                status=status.HTTP_201_CREATED
            )