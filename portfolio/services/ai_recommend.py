from openai import OpenAI
from django.conf import settings
from content_formatter import student_info_to_json, jobs_DB_to_json, owner_info_to_json, students_DB_to_json
from accounts.models import Profile

def recommend_jobs_for_student(student_id, max_tokens=200):
   """
    사용자가 작성한 활동 내용과 관심사를 바탕으로
    업종에 맞는 공고를 추천
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )

    # 해당 대학생
    student_info = Profile.objects.get(id=student_id)
    # 모든 공고
    jobs_queryset = Profile.objects.filter(role='owner')

    messages = [
        {
            "role": "system",
            "content": (
                "당신은 대학생을 위해 최적의 맞춤 공고를 추천하는 AI입니다. "
                "대학생이 설정한 관심 기술, 과거 활동과 공고의 평점, 필요 분야를 참고하여 "
                "가장 알맞은 공고 5개의 id를 반환해주세요."
            )
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "학생 정보:\n"
                        + student_info_to_json(student_info)
                        + "공고들 리스트:\n"
                        + jobs_DB_to_json(jobs_queryset)
                    )
                }
            ]
        }
    ]

    completion = client.chat.completions.create(
        model="google/gemini-2.0-flash-exp:free",
        messages=messages,
        extra_headers={},  # 필요하면 여기에 사이트 URL/제목
        extra_body={}
    )

    return completion.choices[0].message.content

def recommend_jobs_for_student(job_id, max_tokens=200):
   """
    소상공인이 설정한 관심 기술, 도우미의 과거활동, 평점, 관심 분야, 현재 위치를 바탕으로
    알맞는 도우미를 추천
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )

    # 해당 공고
    job_info = Profile.objects.get(id=job_id)
    # 모든 대학생
    students_queryset = Profile.objects.filter(role='student')

    messages = [
         {
            "role": "system",
            "content": (
                "당신은 소상공인을 위해 최적의 대학생 도우미를 추천하는 AI입니다. "
                "소상공인이 설정한 관심 기술, 도우미의 평점, 관심 분야를 참고하여 "
                "가장 알맞은 도우미 5명의 id를 반환해주세요."
            )
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "소상공인 정보:\n"
                        + owner_info_to_json(job_info)
                        + "학생들 리스트:\n"
                        + students_DB_to_json(students_queryset)
                    )
                }
            ]
        }
    ]

    completion = client.chat.completions.create(
        model="google/gemini-2.0-flash-exp:free",
        messages=messages,
        extra_headers={},  # 필요하면 여기에 사이트 URL/제목
        extra_body={}
    )

    return completion.choices[0].message.content
