from rest_framework import serializers
from .models import JobPost, Application
from geopy.distance import geodesic

#전체 조회용
class JobPostListSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    distance_m = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField() 

    class Meta:
        model = JobPost
        fields = ['id', 'company_name', 'description', 'image', 'distance_m','is_liked']
    
    def get_company_name(self, obj):
        if hasattr(obj.owner, 'profile'):
            return obj.owner.profile.company_name
        return

    def get_image(self, obj):
        if obj.image_from_gallery:
            return obj.image_from_gallery.url
        elif obj.image_from_ai:
            return obj.image_from_ai.url
        return None

    def get_distance_m(self, obj):
        request = self.context.get('request')
        if not request:
            return None

        user_lat = request.query_params.get('lat')
        user_lng = request.query_params.get('lng')

        if not user_lat or not user_lng:
            return None

        try:
            user_lat = float(user_lat)
            user_lng = float(user_lng)
            store_lat = obj.store_lat
            store_lng = obj.store_lng

            distance_km = geodesic((user_lat, user_lng), (store_lat, store_lng)).km
            return round(distance_km * 1000)
        except ValueError:
            return None
    def get_description(self, obj):
        # 25자 이상이면 ... 붙이기
        if obj.description:
            return obj.description[:25] + '...' if len(obj.description) > 25 else obj.description
        return ""
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return obj.liked_users.filter(id=user.id).exists()
        return False

#공고 디테일 조회용 - 소상공인
class JobPostSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='owner.profile.company_name', read_only=True)
    business_type = serializers.CharField(source='business_type.profile.company_name', read_only=True)
    ceo_name = serializers.CharField(source='owner.profile.ceo_name', read_only=True)
    address = serializers.CharField(source='owner.profile.location', read_only=True)
    phone_number = serializers.CharField(source='owner.phone', read_only=True)
    business_type = serializers.CharField(source='owner.profile.business_type', read_only=True)
    image = serializers.SerializerMethodField()
    distance_m = serializers.SerializerMethodField()

    class Meta:
        model = JobPost
        fields = [
            'id',
            'company_name',
            'distance_m',
            'ceo_name',
            'business_type',
            'address',
            'phone_number',
            'duration_time',
            'payment_info',
            'description',
            'image',
            'created_at',
            'updated_at',
        ]

    def get_image(self, obj):
        if obj.image_from_gallery:
            return obj.image_from_gallery.url
        elif obj.image_from_ai:
            return obj.image_from_ai.url
        return None

    def get_distance_m(self, obj):
        request = self.context.get('request')
        if not request:
            return None

        user_lat = request.query_params.get('lat')
        user_lng = request.query_params.get('lng')

        if not user_lat or not user_lng:
            return None

        try:
            user_lat = float(user_lat)
            user_lng = float(user_lng)
            store_lat = obj.store_lat
            store_lng = obj.store_lng

            distance_km = geodesic((user_lat, user_lng), (store_lat, store_lng)).km
            return round(distance_km * 1000)
        except ValueError:
            return None

    def validate(self, data):
        # 새로 업로드한 이미지가 없으면 기존 DB 값 확인
        obj = getattr(self, 'instance', None)
        if not self.initial_data.get('image_from_gallery') and not self.initial_data.get('image_from_ai'):
            if not obj or (not obj.image_from_gallery and not obj.image_from_ai):
                raise serializers.ValidationError("이미지는 갤러리 또는 AI 이미지 중 하나는 필수입니다.")
        return data

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.liked_users.filter(id=user.id).exists()
        return False

# 지원서 신청
class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["id", "job_post", "applicant", "motivation", "status", "applied_at"]
        read_only_fields = ["status", "applied_at"]