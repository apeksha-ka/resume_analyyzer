# jobs/urls.py
from django.urls import path
from .views import MatchJobView, ReviewCheckView, AdvancedReviewView,FinalDecisionView, AllProfilesView

urlpatterns = [
    path('match/<int:resume_id>/<int:job_id>/', MatchJobView.as_view()),
    path('api/jobs/match/<int:resume_id>/<int:job_id>/', MatchJobView.as_view()),
    path('jobs/review/<int:resume_id>/', ReviewCheckView.as_view()),
    path('match/<int:resume_id>/<int:job_id>/', MatchJobView.as_view()),
    path('review/<int:resume_id>/', ReviewCheckView.as_view()),
    path('advanced-review/<int:resume_id>/', AdvancedReviewView.as_view()),
    path('final-decision/<int:resume_id>/<int:job_id>/', FinalDecisionView.as_view()),
    path('all-profiles/', AllProfilesView.as_view()),
]