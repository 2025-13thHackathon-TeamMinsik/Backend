from rest_framework import serializers
from .models import Notification
from django.utils import timezone

class NotificationSerializer(serializers.ModelSerializer):
    notification_id = serializers.IntegerField(source='id', read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['notification_id', 'recipient', 'message', 'is_read', 'time_ago', 'created_at']

    def get_time_ago(self, obj):
        now = timezone.now()
        diff = now - obj.created_at
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "방금 전"
        elif seconds < 3600:
            return f"{int(seconds // 60)}분 전"
        elif seconds < 86400:
            return f"{int(seconds // 3600)}시간 전"
        elif seconds < 604800:
            return f"{int(seconds // 86400)}일 전"
        elif seconds < 2592000:
            return f"{int(seconds // 604800)}주 전"
        elif seconds < 31536000:
            return f"{int(seconds // 2592000)}개월 전"
        else:
            return f"{int(seconds // 31536000)}년 전"