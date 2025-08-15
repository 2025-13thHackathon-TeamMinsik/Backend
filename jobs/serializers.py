from rest_framework import serializers
from .models import JobPost
from geopy.distance import geodesic

class JobPostSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='owner.store_name', read_only=True)
    business_type = serializers.CharField(source='owner.business_type', read_only=True)
    address = serializers.CharField(source='owner.address', read_only=True)
    phone_number = serializers.CharField(source='owner.phone_number', read_only=True)
    image = serializers.SerializerMethodField()
    distance_m = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()  

    class Meta:
        model = JobPost
        fields = [
            'id', 'store_name', 'business_type', 'address', 'phone_number',
            'duration_time', 'payment_info', 'payment_type',
            'description', 'image', 'distance_m', 'created_at', 'updated_at',
            'is_liked'
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
