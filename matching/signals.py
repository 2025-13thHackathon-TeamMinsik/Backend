from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MatchRequest
from jobs.models import JobPost, Application
from notifications.models import Notification
from django.contrib.auth import get_user_model
from .utils import generate_nickname

User = get_user_model()

# 학생 -> 공고 지원 시 알림
@receiver(post_save, sender=Application)
def application_created(sender, instance, **kwargs):
    if instance.status == 'pending':
        student = instance.applicant
        job = instance.job_post
        employer = job.owner

        # 학생한테 알림
        Notification.objects.create(
            recipient=student,
            message=f"{employer.profile.company_name} 지원이 완료되었습니다."
        )

        # 소상공인에게
        nickname = generate_nickname()
        Notification.objects.create(
            recipient=employer,
            message=f"{nickname}님이 재능 나누기를 지원했습니다"
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

# 학생이 요청 수락/거절시 알림
@receiver(post_save, sender=MatchRequest)
def match_request_status_changed(sender, instance, **kwargs):
    if not instance._state.adding:  # 기존 객체 업데이트
        helper = instance.helper
        employer = instance.employer
        if instance.status == "accepted":
            Notification.objects.create(
                recipient=employer,
                message=f"{helper.profile.company_name}와 매칭되었어요.\n 연락 후 나눔 진행하세요!\n\n ({helper.phone})"
            )
        elif instance.status == "rejected":
            Notification.objects.create(
                recipient=employer,
                message=f"{helper.profile.company_name} 아쉽게도 매칭되지 않았어요."
            )

# 소상공인이 재능지원함 학생 수락시 알림
@receiver(post_save, sender=Application)
def application_status_changed(sender, instance, **kwargs):
    if not instance._state.adding:
        employer = instance.job_post.owner
        job_post = instance.job_post
        if instance.status == "accepted":
            Notification.objects.create(
                recipient=employer,
                message=f"{employer.profile.company_name}에서 재능을 수락했어요. 의뢰인과 연락하고 나눔을 진행하세요! ({employer.phone})"
            )
        elif instance.status == "rejected":
            Notification.objects.create(
                recipient=employer,
                message=f"{employer.profile.company_name}과/와 아쉽게도 매칭되지 않았어요."
            )