import json
from accounts.models import Profile
from review.models import Review
from jobs.models import JobPost

# 해당 학생 DB 데이터를 Json으로 format
def student_info_to_json(student):
    avg_score = None # 미완성

    skills = list(filter(None, [student.skill_1, student.skill_2]))

    student_dict = {
        "id": student.id,
        "score": avg_score,
        "skills": skills
    }

    return json.dumps(student_dict, ensure_ascii=False)

# 추천할 공고 DB 데이터들을 Json으로 format
# 필요한 데이터: 공고의 평점과 필요 분야
def jobs_DB_to_json(jobs_queryset):
    jobs = []

    for job in jobs_queryset:
        if job.role != 'owner':
            continue

        skills = ", ".join(filter(None, [job.skill_1, job.skill_2]))
        
        jobs.append({
            "id": job.id,
            "skills": skills
        })
    return json.dumps(jobs, ensure_ascii=False)

# 해당 소상공인 DB 데이터를 Json으로 format
def owner_info_to_json(job):
    skills = list(filter(None, [job.skill_1, job.skill_2]))

    return json.dumps(skills, ensure_ascii=False)

# 추천할 학생 DB 데이터들을 Json으로 format
# 필요한 데이터: 학생의 평점과 관심 기술
def students_DB_to_json(students_queryset):
    students = []

    for s in students_queryset:
        if s.role != 'student':
            continue
    
        reviews = Review.objects.filter(student=s.user)
        # 별점 평균 : 미완성

        skills = list(filter(None, [s.skill_1, s.skill_2]))

        students.append({
            "id": s.id,
            "score": avg_score,
            "skills": skills
        })


    return json.dumps(students, ensure_ascii=False)