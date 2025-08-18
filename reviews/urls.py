from django.urls import path
from .views import (
    EmployerReviewCreateView,
    EmployeeReviewCreateView,
    EmployeeReviewListView,
    EmployerReviewListView
)

urlpatterns = [
    path('employer/', EmployerReviewCreateView.as_view(), name='employer-review-create'),
    path('employer/<int:employee_id>/', EmployerReviewListView.as_view(), name='employer-review-list'),
    path('employee/', EmployeeReviewCreateView.as_view(), name='employee-review-create'),
    path('employee/<int:job_id>/', EmployeeReviewListView.as_view(), name='employee-review-list'),
]
