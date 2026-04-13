from django.urls import path
from .views import UploadResumeView, UpdateResumeDetails

urlpatterns = [
    path('upload/', UploadResumeView.as_view()),
    path('update/<int:resume_id>/', UpdateResumeDetails.as_view()),
]