import json
from django.db.models import Avg
from accounts.models import Profile
from reviews.models import EmployerReview, EmployeeReview
from jobs.models import JobPost

# 해당 학생 DB 데이터를 Json으로 format
def student_info_to_json(student):
    skills = list(filter(None, [student.skill_1, student.skill_2]))

    student_dict = {
        "id": student.id,
        "skills": skills
    }

    return json.dumps(student_dict, ensure_ascii=False)

# 추천할 공고 DB 데이터들을 Json으로 format
# 필요한 데이터: 필요 분야, 거리
def jobs_DB_to_json(jobs_queryset):
    jobs = []

    for job in jobs_queryset:
        owner = job.owner
        skills = []
        if hasattr(owner, 'skill_1'):
            skills.append(owner.skill_1)
        if hasattr(owner, 'skill_2'):
            skills.append(owner.skill_2)

        jobs.append({
            "id": job.id,
            "skills": ", ".join(filter(None, skills)) or "기본 기술",
            "latitude": job.store_lat or 0.0,
            "longitude": job.store_lng or 0.0,
        })
    print("공고리스트 최종:", jobs)
    return json.dumps(jobs, ensure_ascii=False)

# 해당 소상공인 DB 데이터를 Json으로 format
def owner_info_to_json(owner_profile):
    skills = list(filter(None, [owner_profile.skill_1, owner_profile.skill_2]))
    
    owner_dict = {
        "id":owner_profile.user.id,
        "skills":skills
    }
    return json.dumps(owner_dict, ensure_ascii=False)

# 추천할 학생 DB 데이터들을 Json으로 format
# 필요한 데이터: 학생의 평점과 관심 기술
def students_DB_to_json(students_queryset):
    students = []

    for s in students_queryset:
        if s.role != 'student':
            continue
    
        # 학생 평점 계산
        reviews = EmployerReview.objects.filter(employee=s.user)
        avg_scores = reviews.aggregate(
            avg_diligence=Avg('diligence'),
            avg_punctuality=Avg('punctuality'),
            avg_cheerful_attitude=Avg('cheerful_attitude'),
            avg_politeness=Avg('politeness'),
        )

        score_values = [v for v in avg_scores.values() if v is not None]
        avg_score = sum(score_values)/len(score_values) if score_values else 0
        skills = list(filter(None, [s.skill_1, s.skill_2]))

        students.append({
            "id": s.id,
            "score": avg_score,
            "skills": skills
        })

    return json.dumps(students, ensure_ascii=False)