import json
import ast
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
from portfolio.models import Portfolio
from reviews.models import EmployerReview
from django.db.models import Avg
from jobs.models import JobPost, Application
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
        
        # 이미 매칭된 상태인지 확인
        if match_request.status == "matched":
            return Response({"error": "이미 매칭이 완료된 요청입니다."}, status=400)

        status_choice = request.data.get("status")

        # accepted인 경우 1:1 매칭 처리
        if status_choice == "accepted":
            return self.handle_match_request_acceptance(match_request)
        else: # rejected인 경우
            match_request.status = "rejected"
            match_request.save()

            serializer = MatchRequestSerializer(match_request)
            return Response(serializer.data)
    
    # 요청 수락시 1:1 메칭 처리
    def handle_match_request_acceptance(self, match_request):
        student = match_request.helper
        employer = match_request.employer
        job_post = match_request.job_post

        # 소상공인이 이미 다른 학생과 매칭되었는지 확인
        existing_owner_match = MatchRequest.objects.filter(
            employer=employer,
            status="matched"
        ).first()

        if existing_owner_match:
            return Response({
                "error": f"소상공인이 이미 다른 학생과 매칭되어 있습니다."
            }, status=400)

        # 학생이 이미 다른 요청과 매칭되었는지 확인
        existing_student_match = MatchRequest.objects.filter(
            helper=student,
            status="matched"
        ).first()

        if existing_student_match:
            return Response({
                "error": f"이미 다른 요청과 매칭되어 있습니다."
            }, status=400)

        # 매칭 성공-상태 변경
        match_request.status = "matched"
        match_request.save()

        # 관련된 Application들 거절 처리
        Application.objects.filter(
            job_post=job_post,
            status="pending"
        ).update(status="rejected")

        Application.objects.filter(
            applicant=student,
            status="pending"
        ).update(status="rejected")

        # 다른 MatchRequest 거절 처리
        MatchRequest.objects.filter(
            employer=employer,
            status="pending"
        ).exclude(id=match_request.id).update(status="rejected")
        
        # 학생이 받은 다른 요청들 거절
        MatchRequest.objects.filter(
            helper=student,
            status="pending"
        ).exclude(id=match_request.id).update(status="rejected")
        
        serializer = MatchRequestSerializer(match_request)
        return Response({
            **serializer.data,
            "message": "매칭이 완료되었습니다! 다른 지원서와 요청들은 자동으로 거절 처리되었습니다."
        })

# 추천 공고
class RecommendJobsView(APIView):
    permission_classes = [IsAuthenticated]    

    def get(self, request):
        user = request.user
        
        # 로그인한 사용자가 학생인지 확인
        try:
            student_profile = Profile.objects.get(user=user, role='student')
        except Profile.DoesNotExist:
            return Response({"error": "학생만 접근 가능합니다."}, status=403)

        # 테스트용: 오늘 추천 체크 로직 주석처리
        # today = timezone.now().date()
        # recommended_jobs_qs = RecommendedJobPost.objects.filter(
        #     student=user,
        #     created_at__date=today
        # )
        # if recommended_jobs_qs.exists():
        #     recommended_jobs = self.get_jobs_detail([r.job_post for r in recommended_jobs_qs])
        #     return Response({"recommended_jobs": recommended_jobs})

        # AI 호출
        try:
            ai_response = recommend_jobs(user.id)  # 로그인한 사용자 ID 전달
            print("AI 반환값:", ai_response)
            
            if isinstance(ai_response, str):
                try:
                    # 마크다운 코드 블록 제거
                    json_str = ai_response.strip()
                    if json_str.startswith('```json'):
                        json_str = json_str.replace('```json', '').replace('```', '').strip()
                    elif json_str.startswith('```'):
                        json_str = json_str.replace('```', '').strip()
                    
                    job_ids = json.loads(json_str)
                    print(f"파싱 성공: {job_ids}")
                except json.JSONDecodeError as e:
                    print(f"JSON 파싱 실패: {e}")
                    print(f"파싱 시도한 문자열: '{json_str}'")
                    job_ids = []
            else:
                job_ids = ai_response
        except Exception as e:
            return Response({"error": f"추천 공고 생성 중 오류 발생: {str(e)}"}, status=500)

        # 디버깅 로그
        print(f"AI가 반환한 job_ids: {job_ids}")
        print(f"job_ids 타입: {type(job_ids)}")

        valid_jobs = []
        for job_id in job_ids:
            print(f"\n=== job_id {job_id} 처리 중 ===")
            try:
                job_post = JobPost.objects.get(id=int(job_id))
                owner_profile = job_post.owner.profile
                print(f"✅ Job Post 찾음: {job_post.owner.profile.company_name}")
                # print(f"✅ Owner Profile 찾음: {owner_user}")
                
                # 테스트용: DB 저장 로직 주석처리
                # RecommendedJobPost.objects.create(student=user, job_post=job_post)
                valid_jobs.append(owner_profile)
                print(f"✅ valid_jobs에 추가됨")
                
            except (User.DoesNotExist, Profile.DoesNotExist):
                print(f"❌ Profile ID {job_id} (role='owner') 찾을 수 없음")
                continue
            except Exception as e:
                print(f"❌ 기타 오류: {e}")
                continue

        print(f"\n최종 valid_jobs 개수: {len(valid_jobs)}")

        if not valid_jobs:
            return Response({
                "recommended_jobs": [],
                "message": "현재 추천할 공고가 없습니다."
            })

        # 공고 정보 가져오기
        recommended_jobs = self.get_jobs_detail(valid_jobs)
        return Response({"recommended_jobs": recommended_jobs})

    def get_jobs_detail(self, owner_profiles):
        jobs_detail = []
        
        for owner_profile  in owner_profiles:
            try:
                owner_jobs = JobPost.objects.get(owner=owner_profile.user)

                # 이미지 우선순위: image_from_ai 먼저, 없으면 image_from_gallery
                job_image = None
                if owner_jobs.image_from_ai:
                    job_image = owner_jobs.image_from_ai.url if hasattr(owner_jobs.image_from_ai, 'url') else owner_jobs.image_from_ai
                elif owner_jobs.image_from_gallery:
                    job_image = owner_jobs.image_from_gallery.url if hasattr(owner_jobs.image_from_gallery, 'url') else owner_jobs.image_from_gallery
                
                job_data = {
                    "id": owner_profile.user.id,
                    "company_name": getattr(owner_profile, "company_name", "알 수 없음"),
                    "description": (getattr(owner_profile, "description", "")[:25] + "...") if getattr(owner_profile, "description", "") else "",
                    "image": job_image,
                    "latitude": getattr(owner_profile, "store_lat", None),
                    "longitude": getattr(owner_profile, "store_lng", None),
                }
                
                jobs_detail.append(job_data)
                
            except Exception as e:
                print(f"소상공인 {owner_profile.user.id} 정보 가져오기 실패: {e}")
                continue
        
        return jobs_detail

# 추천 대학생
# views.py
class RecommendStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 로그인한 사용자가 소상공인인지 확인
        try:
            owner_profile = Profile.objects.get(user=user, role='owner')
        except Profile.DoesNotExist:
            return Response({"error": "소상공인만 접근 가능합니다."}, status=403)

        # 오늘 이미 추천 생성했는지 체크
        # today = timezone.now().date()
        # qs_today = RecommendedStudent.objects.filter(owner=user, created_at__date=today)
        # if qs_today.exists():
        #     recommended_students = [r.student.id for r in qs_today]
        #     return Response({"recommended_students": recommended_students})

        # AI 호출
        try:
            ai_response = recommend_students(owner_profile)  # owner_profile 객체를 그대로 전달
            print("AI 반환값:", ai_response)
            if isinstance(ai_response, str):
                try:
                    student_ids = json.loads(ai_response)
                except json.JSONDecodeError:
                    student_ids = []
            else:
                student_ids = ai_response
        except Exception as e:
            return Response({"error": f"추천 학생 생성 중 오류 발생: {str(e)}"}, status=500)

        # AI 호출 후 추가
        print(f"AI가 반환한 student_ids: {student_ids}")
        print(f"student_ids 타입: {type(student_ids)}")

        valid_students = []
        for student_id in student_ids:
            print(f"\n=== student_id {student_id} 처리 중 ===")
            try:
                student_profile = Profile.objects.get(id=int(student_id), role='student')
                print(f"✅ Profile 찾음: {student_profile}")
                student = student_profile.user
                print(f"✅ User 찾음: {student.full_name}")
                # DB에 저장
                # RecommendedStudent.objects.create(student=student, owner=user)
                valid_students.append(student)
                print(f"✅ valid_students에 추가됨")
            except Profile.DoesNotExist:
                print(f"Profile ID {student_id} 찾을 수 없음")
                continue

        if not valid_students:
            return Response({
                "recommended_students": [],
                "message": "현재 추천할 학생이 없습니다."
            })
        # 학생 정보 가져오기
        recommended_students = self.get_students_detail(valid_students)
        return Response({"recommended_students": recommended_students})


    def get_students_detail(self, students):
        students_detail = []

        for student in students:
            try:
                portfolio = Portfolio.objects.filter(user=student).first()
                profile_image = portfolio.profile_image.url if portfolio and portfolio.profile_image else None
                
                employer_review = EmployerReview.objects.filter(employee=student).first()

                student_data = {
                    "id": student.id,
                    "name": student.full_name,
                    "profile_image": profile_image,
                    "diligence": employer_review.diligence if employer_review else 0,
                    "punctuality": employer_review.punctuality if employer_review else 0,
                    "cheerful_attitude": employer_review.cheerful_attitude if employer_review else 0,
                    "politeness": employer_review.politeness if employer_review else 0,
                }
                students_detail.append(student_data) 
            except Exception as e:
                print(f"학생 {student.id} 정보 가져오기 실패: {e}")
                continue
        
        return students_detail