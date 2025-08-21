from django.urls import path
from . import views

urlpatterns = [
    # 알림 조회
    path('', views.NotificationListView.as_view(), name='notifications'),
    # 알림 읽기
    path('<int:notification_id>/read/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),
]