from django.urls import path
from .views import github_webhook, gitlab_webhook

urlpatterns = [
    path('github', github_webhook, name='github_webhook'),
    path('gitlab', gitlab_webhook, name='gitlab_webhook'),
]
