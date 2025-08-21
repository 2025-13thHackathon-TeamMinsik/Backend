import json
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
from .serializers import MatchRequestSerializer
from notifications.models import Notification
from .models import RecommendedJobPost, RecommendedStudent, MatchRequest
from accounts.models import User, Profile
from .services.ai_recommend import recommend_jobs, recommend_students

# Create your views here.

# 소상공인->학생 재능 요청하기
class MatchRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        employer = request.user
        helper_id = request.data.get('helper_id')
        job_id = request.data.get('job_id')
        match_request, _ = MatchRequest.objects.get_or_create(
            employer=employer,
            helper_id=helper_id,
            job_post_id=job_id
        )
        serializer = MatchRequestSerializer(match_request)
        return Response(serializer.data)

# 학생이 소상공인의 요청 수락/거절 처리
class StudentRespondMatchRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        match_request = get_object_or_404(MatchRequest, id=request_id, helper=request.user)

        # 요청받은 학생만 응답 가능
        if match_request.helper != request.user:
            return Response({"error": "권한이 없습니다."}, status=403)

        status = request.data.get("status")  # 'accepted' or 'rejected'
        match_request.status = status
        match_request.save()

        serializer = MatchRequestSerializer(match_request)
        return Response(serializer.data)

# 추천 공고
class RecommendJobsView(APIView):
    permission_classes = [IsAuthenticated]    

    def get(self, request, student_id):
        # 1. 학생 프로필 확인
        try:
            student_info = Profile.objects.get(user_id=student_id)
        except Profile.DoesNotExist:
            return Response({"error": "해당 학생 프로필이 존재하지 않습니다."}, status=404)

        today = timezone.now().date()

        # 2. 오늘 추천이 이미 존재하는지 확인
        recommended_jobs_qs = RecommendedJobPost.objects.filter(
            student_id=student_info.user.id,
            created_at__date=today
        )

        if recommended_jobs_qs.exists(): # 오늘 추천공고 생성
            # DB에서 가져오기
            recommended_jobs = recommended_jobs_qs
        else:
            # AI 호출 후 추천 생성
            try:
                recommended_job_ids = recommend_jobs(student_info.user.id)
                recommended_jobs = []
                for job_id in recommended_job_ids:
                    job_post = JobPost.objects.get(id=job_id)
                    rjp = RecommendedJobPost.objects.create(
                        student=student_info.user,
                        job_post=job_post
                    )
                    recommended_jobs.append(rjp)
            except Exception as e:
                return Response(
                    {"error": f"추천 공고 생성 중 오류 발생: {str(e)}"},
                    status=500
                )

        # 3. 추천 공고 ID 리스트 반환
        job_ids = [rjp.job_post.id for rjp in recommended_jobs]
        return Response({"recommended_jobs": job_ids})

# 추천 대학생
class RecommendStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        try:
            job_post = JobPost.objects.get(id=job_id)
        except JobPost.DoesNotExist:
            return Response({"error": "해당 공고가 존재하지 않습니다."}, status=404)

        # 오늘 이미 추천 생성했는지 체크
        today = timezone.now().date()
        qs_today = RecommendedStudent.objects.filter(job_post=job_post, created_at__date=today)
        if qs_today.exists():
            # 이미 오늘 생성한 추천이면 DB에서 가져오기
            recommended_students = [r.student.id for r in qs_today]
            return Response({"recommended_students": recommended_students})

        # AI 호출
        try:
            ai_response = recommend_students(job_id)
            student_ids = json.loads(ai_response)  
        except Exception as e:
            return Response({"error": f"추천 학생 생성 중 오류 발생: {str(e)}"}, status=500)

        recommended_students = []
        for student_id in student_ids:
            try:
                student = User.objects.get(id=student_id)
                r = RecommendedStudent.objects.create(student=student, job_post=job_post)
                recommended_students.append(student.id)
            except User.DoesNotExist:
                # 없는 학생이면 무시
                continue

        return Response({"recommended_students": recommended_students})