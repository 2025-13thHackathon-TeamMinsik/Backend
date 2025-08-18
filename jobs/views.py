from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import JobPost
from .serializers import JobPostSerializer,JobPostListSerializer
from django.db.models import Q
from rest_framework.views import APIView
from django.db.models import Count
from geopy.distance import geodesic

class JobPostListView(generics.ListAPIView):
    serializer_class = JobPostListSerializer

    def get_queryset(self):
        queryset = JobPost.objects.select_related('owner__profile').all()
        request = self.request

        # 결제 방식 필터링
        payment_type = request.query_params.get('payment_type')
        if payment_type and payment_type != 'ALL':
            queryset = queryset.filter(payment_type=payment_type)

        # 정렬 옵션
        sort_by = request.query_params.get('sort', 'latest')  # latest, popular, liked, distance
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')

        if sort_by == 'latest':
            queryset = queryset.order_by('-created_at')

        elif sort_by == 'popular':
            queryset = queryset.annotate(applicant_count=Count('applications')).order_by('-applicant_count', '-created_at')

        elif sort_by == 'liked':
            if request.user.is_authenticated:
                queryset = queryset.filter(liked_users=request.user)
            else:
                queryset = queryset.none()

        elif sort_by == 'distance' and lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                queryset = sorted(
                    queryset,
                    key=lambda post: geodesic((lat, lng), (post.store_lat, post.store_lng)).km
                )
            except ValueError:
                pass  # 위도/경도 오류 시 정렬 건너뜀

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class JobPostDetailView(generics.RetrieveAPIView):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

# 공고 작성 (로그인 필요, 최대 1개 제한)
class JobPostCreateView(generics.CreateAPIView):
    serializer_class = JobPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if JobPost.objects.filter(owner=user).exists():
            raise PermissionError("이미 공고를 1개 이상 등록하였습니다.")

        # 모바일에서 받은 GPS 좌표
        store_lat = self.request.data.get('store_lat')
        store_lng = self.request.data.get('store_lng')

        # 이미지 파일 가져오기 (form-data에서 업로드된 경우)
        image_from_gallery = self.request.FILES.get('image_from_gallery')
        image_from_ai = self.request.FILES.get('image_from_ai')

        serializer.save(
            owner=user,
            store_lat=store_lat,
            store_lng=store_lng,
            image_from_gallery=image_from_gallery,
            image_from_ai=image_from_ai
        )

# 공고 수정 (본인 공고만)
class JobPostUpdateView(generics.RetrieveUpdateAPIView):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.owner != self.request.user:
            raise PermissionError("본인이 올린 공고만 수정할 수 있습니다.")
        return obj

# 공고 삭제 (본인 공고만, 이력에서 관리)
class JobPostDeleteView(generics.DestroyAPIView):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.owner != self.request.user:
            raise PermissionError("본인이 올린 공고만 삭제할 수 있습니다.")
        return obj

# 공고 이력 조회 및 선택 삭제
class JobPostHistoryView(generics.ListAPIView):
    serializer_class = JobPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobPost.objects.filter(owner=self.request.user).order_by('-created_at')

 #공고 좋아요   
class JobPostLikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = JobPost.objects.get(pk=pk)

        if post.liked_users.filter(id=request.user.id).exists():
            post.liked_users.remove(request.user)
            liked = False
        else:
            post.liked_users.add(request.user)
            liked = True

        return Response({'liked': liked})

#검색용
class JobPostSearchListView(generics.ListAPIView):
    serializer_class = JobPostListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = JobPost.objects.select_related('owner__profile').all()
        request = self.request

        # 검색 키워드
        keyword = request.query_params.get('q', '').strip()
        if keyword:
            if keyword.startswith('#'):
                keyword = keyword[1:] 
            queryset = queryset.filter(description__icontains=keyword)

        # 결제 방식 필터링
        payment_type = request.query_params.get('payment_type')
        if payment_type and payment_type != 'ALL':
            queryset = queryset.filter(payment_type=payment_type)

        # 정렬 옵션
        sort_by = request.query_params.get('sort', 'latest')  # latest, popular, liked, distance
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')

        if sort_by == 'latest':
            queryset = queryset.order_by('-created_at')

        elif sort_by == 'popular':
            queryset = queryset.annotate(applicant_count=Count('applications')).order_by('-applicant_count', '-created_at')

        elif sort_by == 'liked':
            if request.user.is_authenticated:
                queryset = queryset.filter(liked_users=request.user)
            else:
                queryset = queryset.none()

        elif sort_by == 'distance' and lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                queryset = sorted(
                    queryset,
                    key=lambda post: geodesic((lat, lng), (post.store_lat, post.store_lng)).km
                )
            except ValueError:
                pass  # 위도/경도 오류 시 정렬 건너뜀

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
