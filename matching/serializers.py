from rest_framework import serializers
from jobs.models import Application

# 대학생-재능 나누기
class TalentShareSerializer(serializers.ModelSerializer):
    student_request_status = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ['id', 'student_request_status']

    def get_student_request_status(self, obj):
        return obj.status

# 소상공인-재능 요청하기
class TalentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentRequest
        fields = ['id', 'status']