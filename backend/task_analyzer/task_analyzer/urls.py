# task_analyzer/urls.py

from django.urls import path, include # pyright: ignore[reportMissingModuleSource]

urlpatterns = [
    path("api/tasks/", include("infrastructure.api.urls")),
]
