# task_analyzer/urls.py

from django.urls import path, include

urlpatterns = [
    path("api/tasks/", include("infrastructure.api.urls")),
]
