from rest_framework import serializers
from .models import EmployerReview, EmployeeReview


class EmployerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerReview
        fields = ['job',  'diligence', 'punctuality', 'cheerful_attitude', 'politeness', 'created_at', 'author', 'employee']
        read_only_fields = ('created_at', 'author', 'employee') 

    def validate(self, data):
        for field in ['diligence', 'punctuality', 'cheerful_attitude', 'politeness']:
            if not 1 <= data[field] <= 5:
                raise serializers.ValidationError({field: "1~5 사이의 별점만 가능합니다."})
        return data


class EmployeeReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeReview
        fields = ['job', 'rating', 'content', 'created_at', 'author', 'employer']
        read_only_fields = ('created_at', 'author', 'employer') 

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("1~5 사이의 별점만 가능합니다.")
        return value
