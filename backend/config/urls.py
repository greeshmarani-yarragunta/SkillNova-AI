"""
URL configuration for SkillNova AI platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('health/', health),
    path('admin/', admin.site.urls),

    # SkillNova AI REST API Endpoints
    path('api/', include('accounts.urls')),
    path('api/', include('assessments.urls')),
    path('api/', include('ai.urls')),
    path('api/', include('resumes.urls')),
    path('api/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)