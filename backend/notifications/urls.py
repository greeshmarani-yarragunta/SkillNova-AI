from django.urls import path
from .views import (
    NotificationListView, UnreadNotificationCountView,
    MarkNotificationReadView, MarkAllNotificationsReadView
)

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notification_list'),
    path('notifications/unread-count/', UnreadNotificationCountView.as_view(), name='notification_unread_count'),
    path('notifications/<int:pk>/read/', MarkNotificationReadView.as_view(), name='notification_mark_read'),
    path('notifications/mark-all-read/', MarkAllNotificationsReadView.as_view(), name='notification_mark_all_read'),
]
