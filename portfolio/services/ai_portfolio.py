from openai import OpenAI
from django.conf import settings

def generate_ai_portfolio(job_description, skills, motivation, review):

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )

    system_prompt = """
        당신은 대학생의 포트폴리오를 요약하는 AI입니다.
        조건:
        - **정확히 120자 이내로 작성합니다. 절대 초과하지 마세요.**
        - 대학생이 작성한 후기(활동 소감)를 중심으로 표현합니다.
        - 공고 내용, 지원 동기, 보유 기술은 참고 자료로만 사용합니다.
        - 읽는 사람이 학생의 성실성과 성장을 느낄 수 있도록 매력적으로 작성하세요.
    """

    user_prompt = f"""
        공고 내용: {job_description}
        지원 동기: {motivation}
        후기: {review}
        기술: {skills}
    """

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    completion = client.chat.completions.create(
        model="google/gemini-2.0-flash-exp:free",
        messages=messages,
        extra_headers={},  # 필요하면 여기에 사이트 URL/제목
        extra_body={}
    )

    return completion.choices[0].message.content
