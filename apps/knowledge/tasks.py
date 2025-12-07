from pathlib import Path
import os
import time

from celery import shared_task
from django.contrib.auth import get_user_model
from .rag_service import RAG_Service
from .models import Knowledge

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def ingest_pdf_and_create_knowledge(self, user_id: int,  file_path: str, title: str = "",):
    """
    Tarefa Celery que lê o PDF, executa ingestão (stub) e cria o Knowledge somente após sucesso.
    """
    User = get_user_model()
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado para ingestão: {file_path}")

    user = User.objects.get(pk=user_id)

    try:
        RAG_Service.ingest_pdf(str(file_path), str(user_id), title)
        knowledge = Knowledge.objects.create(user=user, title=title)
        
    finally:
        file_path_str = str(file_path)
        if os.path.exists(file_path_str):
            try:
                time.sleep(0.5)
                os.remove(file_path_str)
            except PermissionError:
                print("PermissionError")
                time.sleep(2)
                try:
                    os.remove(file_path_str)
                except Exception:
                    print("Exception")
                    pass
            except Exception:
                print("Exception 01")
                pass

    return {"status": "success", "user_id": user_id}
