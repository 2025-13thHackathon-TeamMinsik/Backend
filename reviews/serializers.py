from rest_framework import serializers
from .models import EmployerReview, EmployeeReview
from jobs.models import Application
from matching.models import MatchRequest

class EmployerReviewSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = EmployerReview
        fields = ['job',  'diligence', 'punctuality', 'cheerful_attitude', 'politeness', 'created_at', 'author', 'employee', 'status']
        read_only_fields = ('created_at', 'author', 'employee') 

    def validate(self, data):
        for field in ['diligence', 'punctuality', 'cheerful_attitude', 'politeness']:
            if not 1 <= data[field] <= 5:
                raise serializers.ValidationError({field: "1~5 사이의 별점만 가능합니다."})
        return data

    def get_status(self, obj):
        """해당 후기와 관련된 작업 상태 반환"""
        # Application에서 상태 찾기
        application = Application.objects.filter(
            applicant=obj.employee,  # 학생
            job_post=obj.job      # 공고
        ).first()
        
        if application:
            return {
                'type': 'application',
                'status': application.status,
            }
        
        # MatchRequest에서 상태 찾기
        match_request = MatchRequest.objects.filter(
            helper=obj.employee,    # 학생
            job_post=obj.job,     # 공고
        ).first()
        
        if match_request:
            return {
                'type': 'match_request',
                'status': match_request.status,
            }
        
        return {
            'type': 'unknown',
            'status': 'unknown',
        }


class EmployeeReviewSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeReview
        fields = ['job', 'rating', 'content', 'created_at', 'author', 'employer', 'status']
        read_only_fields = ('created_at', 'author', 'employer') 

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("1~5 사이의 별점만 가능합니다.")
        return value

    def get_status(self, obj):
        """해당 후기와 관련된 작업 상태 반환"""
        # Application에서 상태 찾기
        application = Application.objects.filter(
            applicant=obj.author,  # 학생
            job_post=obj.job  # 공고
        ).first()
        
        if application:
            return {
                'type': 'application',
                'status': application.status,
            }
        
        # MatchRequest에서 상태 찾기
        match_request = MatchRequest.objects.filter(
            helper=obj.author,     # 학생
            employer=obj.employer,     # 소상공인
            job_post=obj.job       # 공고
        ).first()
        
        if match_request:
            return {
                'type': 'match_request',
                'status': match_request.status,
            }
        
        return {
            'type': 'unknown',
            'status': 'unknown',
        }
