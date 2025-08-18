from django.urls import path
from portfolio.views import PortfolioRetrieveAPIView, PortfolioBasicUpdateAPIView, PortfolioIntroduceUpdateAPIView, ActivityUpdateAPIView, TalentImageCreateAPIView, TalentImageDeleteAPIView

urlpatterns = [
    path('', PortfolioRetrieveAPIView.as_view(), name='portfolio-retrieve'),
    path('images/add/', TalentImageCreateAPIView.as_view(), name='portfolio-image-add'),
    path('images/delete/<int:image_id>/', TalentImageDeleteAPIView.as_view(), name='portfolio-image-delete'),
    path('update/basic/', PortfolioBasicUpdateAPIView.as_view(), name='portfolio-update-basic'),
    path('update/introduce/', PortfolioIntroduceUpdateAPIView.as_view(), name='portfolio-update-introduce'),
    path('update/activity/<int:activity_id>/', ActivityUpdateAPIView.as_view(), name='portfolio-update-activity'),
] 