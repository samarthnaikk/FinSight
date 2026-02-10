from django.urls import path
from .views import AIIngestView, ChatMessageView

urlpatterns = [
    path("ai/ingest/", AIIngestView.as_view(), name="ai-ingest"),
    path("chat/message/", ChatMessageView.as_view(), name="chat-message"),
]
