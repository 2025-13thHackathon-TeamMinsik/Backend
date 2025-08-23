from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import JobPost, Application
from .serializers import JobPostSerializer,JobPostListSerializer,ApplicationSerializer
from django.db.models import Q
from rest_framework.views import APIView
from django.db.models import Count
from geopy.distance import geodesic
from matching.utils import generate_nickname
from notifications.models import Notification

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

# 학생 -> 공고 지원
class ApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        job = get_object_or_404(JobPost, id=job_id)
        applicant = request.user  # 지원하는 학생 (로그인 사용자)
        motivation = request.data.get('motivation', '')

        application, created = Application.objects.get_or_create(
            job_post=job,
            applicant=applicant,
            defaults={"motivation": motivation}
        )

        if not created and motivation:
            application.motivation = motivation
            application.save()

        serializer = ApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

# 소상공인이 공고에 지원한 학생 수락/거절 처리
class AcceptApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        application = get_object_or_404(Application, id=application_id)
        job_owner = application.job_post.owner

        # 해당 공고 소상공인만 수락/거절 가능
        if request.user != job_owner:
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        # 수락/거절 두 가지만 가능
        status_choice = request.data.get("status")
        if status_choice not in ["accepted", "rejected"]:
            return Response({"error": "status는 accepted 또는 rejected만 가능합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 이미 매칭된 상태인지 확인
        if application.status == "matching":
            return Response({"error": "이미 매칭이 완료된 지원서입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        if status_choice == "accepted":
            return self.handle_matching(application, job_owner)
        else:
            application.staus = "rejected"
            application.save()

            return Response({
                "id": application.id,
                "job_post": application.job_post.id,
                "applicant": application.applicant.id,
                "status": application.status,
                "message": f"지원서가 거절되었습니다."
            }, status-status.HTTP_200_OK)

        # 상태 저장
        application.status = status_choice
        application.save()

        return Response({
            "id": application.id, # 지원서 id
            "job_post": application.job_post.id,
            "application": application.applicant.id,
            "status": application.status,
            "message": f"Application이 {application.status} 처리 되었습니다."
        }, status=status.HTTP_200_OK)

    # 1:1 매칭 처리 로직
    def handle_matching(self, application, job_owner):
        student = application.applicant
        job_post = application.job_post

        # 소상공인(공고)이 이미 다른 학생과 매칭 되었는지 확인
        existing_owner_match = Application.objects.filter(
            job_post__owner = job_owner,
            status="matching"
        ).first()

        if existing_owner_match:
            return Response({
                "error": f"이미 다른 학생({existing_owner_match.applicant.full_name})과 매칭되어 있습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 학생이 이미 다른 공고와 매칭되었는지 확인
        existing_student_match = Application.objects.filter(
            applicant=student,
            status="matching"
        ).first()

        if existing_student_match:
            return Response({
                "error": f"해당 학생이 이미 공고와 매칭되어 있습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 매칭 성공 - 상태 변경
        application.status = "matching"
        application.save()

        # 해당 공고의 다른 지원자들 모두 거절 처리
        other_applications = Application.objects.filter(
            job_post=job_post,
            status="pending"
        ).exclude(id=application.id)

        other_applications.update(status="rejected")

        # 해당 학생의 다른 지원서들 모두 거절 처리
        student_other_applications = Application.objects.filter(
            applicant=student,
            status="pending"
        ).exclude(id=application.id)

        student_other_applications.update(status="rejected")

        # 요청들 모두 거절 처리
        MatchRequest.objects.filter(
            employer=job_owner,
            status="pending"
        ).update(status="rejected")
        
        # 학생이 받은 다른 요청들 거절
        MatchRequest.objects.filter(
            helper=student,
            status="pending"
        ).update(status="rejected")
        
        return Response({
            "id": application.id,
            "job_post": application.job_post.id,
            "applicant": application.applicant.id,
            "status": application.status,
            "message": f"매칭이 완료되었습니다! 다른 지원서들은 자동으로 거절 처리되었습니다."
        }, status=status.HTTP_200_OK)