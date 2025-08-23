from rest_framework import serializers
from jobs.models import JobPost, Application
from accounts.models import Profile, User
from portfolio.models import Portfolio, Activities, TalentImage
from reviews.models import EmployerReview
from django.db.models import Avg

# 재능 지원함
class JobAndRequestedSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField(source='id', read_only=True)
    # 재능 도우미(공고에 신청한 대학생 리스트)
    applicants = serializers.SerializerMethodField()
    
    class Meta:
        model = JobPost
        fields = ['job_id', 'duration_time', 'payment_info', 'payment_type', 'description', 'applicants']

    def get_applicants(self, obj):
        applications = obj.applications.select_related('applicant', 'applicant__profile')
        applicants = []

        for app in applications:
            user = app.applicant
            profile = getattr(user, 'profile', None)

            # 각 항목의 평균 별점 계산
            avg_scores = EmployerReview.objects.filter(employee=user).aggregate(
                avg_participation=Avg('participation'),
                avg_diligence=Avg('diligence'),
                avg_punctuality=Avg('punctuality'),
                avg_cheerful_attitude=Avg('cheerful_attitude'),
                avg_politeness=Avg('politeness')
            )

            # 프로필 이미지 가져오기
            portfolio = getattr(user, 'portfolio', None)
            profile_image_url = None
            if portfolio and portfolio.profile_img:
                profile_image_url = portfolio.profile_img.url

            applicant_data = {
                'application_id': app.id,
                'user_id': user.id,
                'name': user.full_name,
                'profile_image': profile_image_url,
                'university': profile.university if profile else None,
                'major': profile.major if profile else None,
                'academic_status': profile.academic_status if profile else None,
                # 평가 점수들
                'participation_score': round(avg_scores['avg_participation'] or 0, 1),
                'diligence_score': round(avg_scores['avg_diligence'] or 0, 1),
                'punctuality_score': round(avg_scores['avg_punctuality'] or 0, 1),
                'cheerful_attitude_score': round(avg_scores['avg_cheerful_attitude'] or 0, 1),
                'politeness_score': round(avg_scores['avg_politeness'] or 0, 1),
                'applied_at': app.applied_at,
            }
            applicants.append(applicant_data)
        
        return applicants

# 지원자 상세 보기
class StudentDetailSerializer(serializers.ModelSerializer):
    application_id = serializers.IntegerField(source='id', read_only=True)
    # 나눔 동기
    motivation = serializers.CharField(source='job_post.application.motivation', read_only=True)
    # 지원자 정보
    applicant_info = serializers.SerializerMethodField()
    # 포트폴리오 정보(기본정보/자기소개/활동이력/재능관람)
    portfolio = serializers.SerializerMethodField()
    # 활동이력
    activity_history = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ['application_id', 'motivation', 'applicant_info', 'portfolio', 'activity_history', 'applied_at']

    def get_applicant_info(self, obj):
        user = obj.applicant
        profile = getattr(user, 'profile', None)

        return {
            'user_id': user.id,
            'name': user.full_name,
            'email': user.email,
            'phone': user.phone,
            'birth': user.birth,
            'gender': profile.gender if profile else None,
            'university': profile.university if profile else None,
            'major': profile.major if profile else None,
            'academic_status': profile.academic_status if profile else None,
            'location': profile.location if profile else None,
            'skill_1': profile.get_skill_1_display() if profile else None,
            'skill_2': profile.get_skill_2_display() if profile else None,
        }

    def get_portfolio(self, obj):
        try:
            portfolio = Portfolio.objects.get(user=obj.applicant)

            # 재능 이미지
            talent_images = []
            for image in portfolio.images.all():
                if image.image:
                    talent_images.append(image.image.url)
            
            return {
                'profile_img': portfolio.profile_img.url if portfolio.profile_img else None,
                'self_introduce': portfolio.self_introduce,
                'talent_url': portfolio.talent_url,
                'talent_images': talent_images,
            }
        except Portfolio.DoesNotExist:
            return {
                'profile_img': None,
                'self_introduce': None,
                'talent_url': None,
                'talent_images': [],
            }

    def get_activity_history(self, obj):
        activities = Activities.objects.filter(portfolio__user=obj.applicant).select_related('job', 'application').order_by('-job__created_at')

        activity_list = []
        for activity in activities:
            activity_data = {
                'job_id': activity.job.id,
                'company_name': activity.job.owner.profile.company_name if hasattr(activity.job.owner, 'profile') else activity.job.owner.full_name,
                'duration_time': activity.job.duration_time,
                'payment_type': activity.job.get_payment_type_display(),
                'ai_portfolio_summary': activity.ai_portfolio_summary,
                'completed_at': activity.job.created_at,  # 실제로는 완료일시 필드가 필요할 수 있음
            }
            activity_list.append(activity_data)
        
        return activity_list

# 재능 요청하기
# class RequestTalentSerializer(serializers.ModelSerializer):
