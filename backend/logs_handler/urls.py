# urls.py
from django.urls import path
from .views import FetchLogs, IngestLogs

urlpatterns = [
    path('filter/', FetchLogs.as_view()),
    path('ingest/', IngestLogs.as_view())
]
