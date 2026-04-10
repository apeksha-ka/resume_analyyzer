# jobs/urls.py
from django.urls import path
from .views import MatchJobView

urlpatterns = [
    path('match/<int:resume_id>/<int:job_id>/', MatchJobView.as_view()),
    path('api/jobs/match/<int:resume_id>/<int:job_id>/', MatchJobView.as_view()),
]