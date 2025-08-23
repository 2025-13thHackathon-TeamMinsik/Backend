from rest_framework import serializers
from jobs.models import Application
from .models import MatchRequest

# 소상공인->학생 재능 요청
class MatchRequestSerializer(serializers.ModelSerializer):
    request_id = serializers.IntegerField(source='id', read_only=True)
    class Meta:
        model = MatchRequest
        fields = ['request_id', 'employer', 'helper', 'job_post', 'status', 'created_at']

# 대학생-재능 나누기
class TalentShareSerializer(serializers.ModelSerializer):
    request_id = serializers.IntegerField(source='id', read_only=True)
    student_request_status = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ['request_id', 'student_request_status']

    def get_student_request_status(self, obj):
        return obj.status