import json
from jobs.models import JobPost
from portfolio.models import Portfolio
from review.models import StudentReview

# 필요한 데이터: 나눔 내용, 나눔 동기, 대학생의 활동 후기
def portfolio_input_data(job_post, application, review):
    data = {
        "job_description": job_post.jobDescription,
        "motivation": application.motivation,
        "student_review": review.review_content
    }
    return json.dumps(data, ensure_ascii=False)