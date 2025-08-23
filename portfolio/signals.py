from django.db.models.signals import post_save
from django.dispatch import receiver
from reviews.models import EmployeeReview
from .models import Activities
from .services.ai_portfolio import generate_ai_portfolio

# 리뷰 작성되면 AI 포트폴리오 작성 함수 호출
@receiver(post_save, sender=EmployeeReview)
def create_ai_portfolio(sender, instance, created, **kwargs):
    if created:
        try:
            # EmployeeReview에서 직접 job에 접근
            job = instance.job
            employee = instance.employee
            
            # 해당 job에 대한 employee의 지원서(Application) 찾기
            try:
                application = Application.objects.get(
                    applicant=employee,
                    job=job
                )
            except Application.DoesNotExist:
                print(f"Application not found for employee {employee.id} and job {job.id}")
                return
            
            # 해당 지원서와 연관된 Activities 찾기
            try:
                activity = Activities.objects.get(
                    application=application,
                    job=job
                )
            except Activities.DoesNotExist:
                print(f"Activity not found for application {application.id}")
                return
            
            # 안전한 데이터 접근
            job_description = job.description or ""
            
            # profile이나 skill이 없을 경우 처리
            profile = getattr(employee, 'profile', None)
            if profile:
                skill_1 = getattr(profile, 'skill_1', '') or ''
                skill_2 = getattr(profile, 'skill_2', '') or ''
                skills = f"{skill_1}, {skill_2}".strip(', ')
            else:
                skills = ""
            
            motivation = getattr(application, 'motivation', '') or ""
            review_content = instance.content or ""
            
            # AI 포트폴리오 생성 함수 호출
            ai_summary = generate_ai_portfolio(
                job_description=job_description,
                skills=skills,
                motivation=motivation,
                review=review_content
            )
            
            activity.ai_portfolio_summary = ai_summary
            activity.save()
            
        except Exception as e:
            # 기타 예외 처리
            print(f"Error creating AI portfolio: {e}")
