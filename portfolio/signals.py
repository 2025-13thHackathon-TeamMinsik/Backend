from django.db.models.signals import post_save
from django.dispatch import receiver
from reviews.models import EmployeeReview
from .models import Activities
from .services.ai_portfolio import generate_ai_portfolio

# 리뷰 작성되면 AI 포트폴리오 작성 함수 호출
@receiver(post_save, sender=EmployeeReview)
def create_ai_portfolio(sender, instance, created, **kwargs):
    if not created:
        return

    if not hasattr(instance, 'activity') or instance.activity is None:
        return

    try:
        activity = instance.activity
    except Activities.DoesNotExist:
        return

    # 공고 내용
    job_description = activity.job.description 
    # 기술
    skills = f"{activity.application.user.profile.skill_1}, {activity.application.user.profile.skill_2}"
    # 지원 동기
    motivation = activity.application.motivation 
    # 후기
    review_content = instance.content

    # AI 포트폴리오 생성 함수 호출
    ai_summary = generate_ai_portfolio(
        job_description=job_description,
        skills=skills,
        motivation=motivation,
        review=review_content
    )

    activity.ai_portfolio_summary = ai_summary
    activity.save()
