from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MatchRequest
from jobs.models import JobPost, Application
from notifications.models import Notification
from reviews.models import EmployerReview, EmployeeReview
from django.contrib.auth import get_user_model
from .utils import generate_nickname

User = get_user_model()

# 학생 -> 공고 지원 시 알림
@receiver(post_save, sender=Application)
def application_created(sender, instance, created, **kwargs):
    if created and instance.status == 'pending': # 새로 지원 생성됨
        student = instance.applicant
        job = instance.job_post
        employer = job.owner

        # 닉네임 생성 및 저장
        nickname = generate_nickname()
        instance.nickname = nickname
        instance.save(update_fields=['nickname'])

        # 학생한테 알림
        Notification.objects.create(
            recipient=student,
            message=f"{employer.profile.company_name} 지원이 완료되었습니다."
        )

        # 소상공인에게
        nickname = generate_nickname()
        Notification.objects.create(
            recipient=employer,
            message=f"{nickname}님이 재능 나누기를 지원했습니다."
        )

# 소상공인 -> 추천 학생 요청 시 알림
@receiver(post_save, sender=MatchRequest)
def notify_match_request(sender, instance, created, **kwargs):
    if created and instance.status == "pending":
        employer = instance.employer
        helper = instance.helper

        Notification.objects.create(
            recipient=helper,  # 알림 받는 사람: 추천 학생
            message=f"{employer.profile.company_name}에서 재능을 요청했어요!"
        )

# 학생이 요청 수락/거절시 알림(소상공인한테)
@receiver(post_save, sender=MatchRequest)
def match_request_status_changed(sender, instance, **kwargs):
    if not instance._state.adding:  # 기존 객체 업데이트
        helper = instance.helper # 학생
        employer = instance.employer
        
        # 해당 지원서의 닉네임 가져오기
        try: 
            application = Application.objects.get(
                applicant=helper,
                job_post=instance.job_post
            )
            nickname = application.nickname
        except Application.DoesNotExist:
            nickname="익명의 도우미"

        if instance.status == "matched": # 수락 시
            Notification.objects.create(
                recipient=employer,
                message=f"{helper.profile.company_name}와 매칭되었어요.\n 도우미와 연락 후 나눔 진행하세요!\n\n ({helper.phone})"
            )
        elif instance.status == "rejected": # 거절 시
            Notification.objects.create(
                recipient=employer,
                message=f"{helper.profile.company_name}과/와 아쉽게도 매칭되지 않았어요."
            )

# 소상공인이 재능지원함 학생 수락시 알림(학생한테)
@receiver(post_save, sender=Application)
def application_status_changed(sender, instance, **kwargs):
    if not instance._state.adding:
        student = instance.applicant #지원한 학생
        employer = instance.job_post.owner
        job_post = instance.job_post
        if instance.status == "matched": # 수락 시
            Notification.objects.create(
                recipient=student,
                message=f"{employer.profile.company_name}에서 재능을 수락했어요. 의뢰인과 연락하고 나눔을 진행하세요! ({employer.phone})"
            )
        elif instance.status == "rejected": # 거절 시
            Notification.objects.create(
                recipient=student,
                message=f"{employer.profile.company_name}과/와 아쉽게도 매칭되지 않았어요."
            )

# 소상공인이 후기 작성->학생에게 후기 작성하라는 알림
@receiver(post_save, sender=EmployerReview)
def notifiy_review(sender, instance, created,**kwargs):
    if created:
        student = instance.employee
        company_name = instance.author.profile.company_name
        
        # 이미 같은 내용의 알림이 있는지 확인
        message = f"{company_name} 작업을 마치셨나요? 후기를 작성해보세요."
        
        # 중복 알림 방지
        if not Notification.objects.filter(
            recipient=student,
            message=message,
            is_read=False
        ).exists():
            Notification.objects.create(
                recipient=student,
                message=message
            )

# 학생 후기 작성 완료 -> 모두 작업 완료 처리
@receiver(post_save, sender=EmployeeReview)
def complete_application(sender, instance, created, **kwargs):
    if created:
        try:
            # 해당 학생과 공고에 대한 Application 찾기
            application = Application.objects.filter(
                applicant=instance.author,  # 학생 (후기 작성자)
                job_post=instance.job,      # 공고
                status='matched'            # 매칭 완료 상태만
            ).first()

            # 2. MatchRequest 찾기 (소상공인이 요청한 경우)
            match_request = MatchRequest.objects.filter(
                helper=instance.author,     # 학생 (후기 작성자)
                job_post=instance.job,      # 공고
                status='matched'            # 매칭 완료 상태만
            ).first()
            
            if application:
                # 작업 완료로 상태 변경
                application.status = 'completed'
                application.save()
                
                print(f"✅ Application {application.id} 상태가 completed로 변경됨")

            # MatchRequest 완료 처리
            if match_request:
                match_request.status = 'completed'
                match_request.save()
                print(f"✅ MatchRequest {match_request.id} 상태가 completed로 변경됨")
                
            else:
                print(f"❌ 해당하는 매칭된 Application을 찾을 수 없음 (학생: {instance.author}, 공고: {instance.job})")
                
        except Exception as e:
            print(f"❌ 학생 후기 완료 처리 실패: {e}")