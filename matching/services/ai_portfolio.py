from openai import OpenAI
from django.conf import settings
from jobs.models import JobPost, Application
from reviews.models import StudentReview
from content_formatter import portfolio_input_data

def generate_portfolio(user, job_post,max_tokens=100):
    # 지원 정보 가져오기
    application = Application.objects.get(user=user, job_post=job_post)
    # 리뷰 가져오기
    review = StudentReview.objects.filter(user=user, job_post=job_post).first()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )

    messages = [
        {
            "role": "system",
            "content": (
                "당신은 120자 이내의 창의적인 포트폴리오 문장을 작성하는 AI입니다."
                "나눔 내용, 나눔 동기, 대학생의 활동 후기를 토대로 포트폴리오를 작성해주세요"
                "대학생의 후기를 위주로 작성해주세요"
            )
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": portfolio_input_data(job_post, application, review)
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
