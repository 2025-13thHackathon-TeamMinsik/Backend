from django.urls import path
from .views import SignupView, LoginView, BusinessCertUploadView

urlpatterns =[
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('business-cert/', BusinessCertUploadView.as_view(), name='business-cert'),
]

