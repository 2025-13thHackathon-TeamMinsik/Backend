from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    notification_id = serializers.IntegerField(source='id', read_only=True)
    class Meta:
        model = Notification
        fields = ['notification_id', 'recipient', 'message', 'is_read', 'created_at']