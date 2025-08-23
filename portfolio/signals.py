from django.db.models.signals import post_save
from django.dispatch import receiver
from reviews.models import EmployeeReview
from .models import Portfolio, Activities
from jobs.models import Application
from .services.ai_portfolio import generate_ai_portfolio

# 리뷰 작성되면 AI 포트폴리오 작성 함수 호출
@receiver(post_save, sender=EmployeeReview)
def create_ai_portfolio(sender, instance, created, **kwargs):
    print(f"Signal triggered! created: {created}")
    
    if created:
        try:
            job = instance.job
            employee = instance.author
            print(f"Employee: {employee.id}, Job: {job.id}")
            
            # Portfolio가 없으면 생성
            portfolio, portfolio_created = Portfolio.objects.get_or_create(user=employee)
            print(f"Portfolio: {portfolio.id}, Created: {portfolio_created}")
            
            #  Application 찾기 또는 생성
            application, app_created = Application.objects.get_or_create(
                applicant=employee,
                job_post=job,
                defaults={
                    'status': 'matching'  # 또는 적절한 상태
                }
            )
            print(f"Application: {application.id}, Created: {app_created}")
            
            # 해당 지원서와 연관된 Activities 찾기 또는 생성
            activity, activity_created = Activities.objects.get_or_create(
                application=application,
                job=job,
                defaults={
                    'portfolio': portfolio
                }
            )
            print(f"Activity: {activity.id}, Created: {activity_created}")
            
            # 나머지 로직...
            job_description = job.description or ""
            
            profile = getattr(employee, 'profile', None)
            if profile:
                skill_1 = getattr(profile, 'skill_1', '') or ''
                skill_2 = getattr(profile, 'skill_2', '') or ''
                skills = f"{skill_1}, {skill_2}".strip(', ')
            else:
                skills = ""
            
            motivation = getattr(application, 'motivation', '') or ""
            review_content = instance.content or ""
            
            print(f"Data - Job: {job_description[:50]}..., Skills: {skills}, Motivation: {motivation[:50]}...")
            
            # AI 포트폴리오 생성 함수 호출
            ai_summary = generate_ai_portfolio(
                job_description=job_description,
                skills=skills,
                motivation=motivation,
                review=review_content
            )
            
            print(f"AI Summary generated: {ai_summary}")
            
            activity.ai_portfolio_summary = ai_summary
            activity.save()
            
            print(f"✅ AI portfolio saved for activity {activity.id}")
            
        except Exception as e:
            print(f"❌ Error creating AI portfolio: {e}")
            import traceback
            traceback.print_exc()