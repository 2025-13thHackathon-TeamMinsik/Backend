from rest_framework import serializers
from jobs.models import Application
from .models import MatchRequest

# 소상공인->학생 재능 요청
class MatchRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchRequest
        fields = ['id', 'employer', 'helper', 'job_post', 'status', 'created_at']

# 대학생-재능 나누기
class TalentShareSerializer(serializers.ModelSerializer):
    student_request_status = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ['id', 'student_request_status']

    def get_student_request_status(self, obj):
        return obj.status