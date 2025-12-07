from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KnowledgeViewSet, MessageViewSet


router = DefaultRouter()
router.register(r'knowledge', KnowledgeViewSet, basename='knowledge')
router.register(r'message', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]

