from openai import OpenAI
from django.conf import settings
from .content_formatter import student_info_to_json, jobs_DB_to_json, owner_info_to_json, students_DB_to_json
from accounts.models import Profile

# 공고 추천하기
def recommend_jobs(user_id, max_tokens=200):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )

    # User ID 기준 Profile 조회
    try:
        student_info = Profile.objects.get(user_id=user_id)
    except Profile.DoesNotExist:
        return {"error": "해당 학생 프로필이 존재하지 않습니다."}

    # 모든 공고
    jobs_queryset = Profile.objects.filter(role='owner')

    messages = [
        {
            "role": "system",
            "content": (
                "당신은 대학생을 위해 최적의 맞춤 공고를 추천하는 AI입니다. "
                "대학생이 설정한 관심 기술, 공고와의 거리(근거리순), 공고의 업종을 참고하여 "
                "가장 알맞은 공고 5개의 id만 JSON 배열 형식으로 반환해주세요. 예: [1, 2, 3, 4, 5]"
                "만약 공고의 개수가 5개보다 적다면 모두 반환해 주세요."
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

# 대학생 추천하기
def recommend_students(job_id, max_tokens=200):
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
                "가장 알맞은 대학생 5명의 id만 JSON 배열 형식으로 반환해주세요. 예: [1, 2, 3, 4, 5]"
                "만약 대학생이 5명보다 적다면 모두 반환해 주세요."
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
