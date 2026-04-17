from rest_framework.views import APIView
from rest_framework.response import Response
from resumes.models import Resume
from .models import Job
import re
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
def home(request):
    return render(request, 'index.html')

SYNONYMS = {
    "ml": ["machine learning"],
    "nlp": ["natural language processing"],
    "js": ["javascript"]
}

def calculate_decision(resume, job):

    resume_skills = resume.skills.lower().replace(" ", "").split(",")
    job_skills = job.required_skills.lower().replace(" ", "").split(",")

    matched = list(set(resume_skills) & set(job_skills))

    score = round((len(matched) / len(resume_skills)) * 100) if resume_skills else 0

    if score < 40:
        level = "Low"
    elif score <= 70:
        level = "Average"
    else:
        level = "High"

    has_project = bool(resume.projects and resume.projects.strip())
    has_internship = bool(resume.internship and resume.internship.strip())

    if score < 40:
        decision = "Rejected "

    elif score > 75:
        decision = "Shortlisted "

    else:
        if has_project and has_internship:
            decision = "Shortlisted (After Review) "
        else:
            decision = "Rejected (After Review) "

    return score, decision   

class MatchJobView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, resume_id, job_id):

        resume = get_object_or_404(Resume, id=resume_id)
        job = get_object_or_404(Job, id=job_id)

        resume_skills = [s.strip().lower() for s in resume.skills.split(",")] if resume.skills else []
        job_skills = [s.strip().lower() for s in job.required_skills.split(",")]

        matched = list(set(resume_skills) & set(job_skills))

        score = round((len(matched) / len(resume_skills)) * 100) if resume_skills else 0

        if score < 40:
            level = "Low"
        elif score <= 70:
            level = "Average"
        else:
            level = "High"

        # 🎯 Decision
        if score < 40:
            decision = "Rejected "
        elif level == "High":
            decision = "Shortlisted "
        else:
            decision = "Shortlisted (After Review) "

        # 👤 Jobseeker → only status
        if request.user.role == 'jobseeker':
            return Response({
                "status": "Profile under review" if level == "Average" else decision
            })

        # 🏢 Recruiter → full info
        return Response({
            "resume_id": resume.id,
            "user": resume.user.username,
            "score": score,
            "level": level,
            "status": "Review Required" if level == "Average" else "Auto Decision"
        })
        
class ReviewCheckView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request, resume_id):

        # 👤 Jobseeker → only own + hide review
        if request.user.role == 'jobseeker':
            resume = Resume.objects.get(id=resume_id, user=request.user)

            return Response({
                "projects": resume.projects,
                "internship": resume.internship,
                "message": "Profile under review"
            })

        # 🏢 Recruiter → full access
        resume = Resume.objects.get(id=resume_id)

        has_project = bool(resume.projects.strip()) if resume.projects else False
        has_internship = bool(resume.internship.strip()) if resume.internship else False

        if has_project and has_internship:
            review = "Strong Candidate "
        elif has_project or has_internship:
            review = "Average Candidate "
        else:
            review = "Weak Candidate "

        return Response({
            "projects": resume.projects,
            "internship": resume.internship,
            "review": review
        })
    
class AdvancedReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, resume_id):

        # 👤 Jobseeker → BLOCK access
        if request.user.role != 'recruiter':
            return Response({
                "error": "Only recruiters can view advanced analysis"
            }, status=403)

        # 🏢 Recruiter → full access
        resume = Resume.objects.get(id=resume_id)

        if resume.projects and "django" in resume.projects.lower():
            skill_depth = "Strong "
        else:
            skill_depth = "Basic "

        if len(resume.extracted_text) > 500:
            quality = "Good "
        else:
            quality = "Poor "

        extras = []
        if resume.certifications:
            extras.append("Certifications ")
        if resume.github:
            extras.append("GitHub ")

        return Response({
            "skill_depth": skill_depth,
            "resume_quality": quality,
            "extras": extras if extras else "No extras "
        })
class FinalDecisionView(APIView):
   def get(self, request, resume_id):

    resume = Resume.objects.get(id=resume_id)
    job = Job.objects.first()

    resume_skills = [s.strip().lower() for s in resume.skills.split(",") if s.strip()] if resume.skills else []
    job_skills = [s.strip().lower() for s in job.required_skills.split(",") if s.strip()]

    matched = list(set(resume_skills) & set(job_skills))
    
    score = round((len(matched) / len(job_skills)) * 100) if job_skills else 0
    if score < 40:
        level = "Low"
    elif score <= 70:
        level = "Average"
    else:
        level = "High"

    # 🎯 SAME DECISION AS PROFILE VIEW
    if score < 40:
     decision = "Rejected "

    elif score >= 70:
         decision = "Shortlisted "   # 🔥 direct shortlist

    else:
       has_project = bool(resume.projects and resume.projects.strip())
       has_internship = bool(resume.internship and resume.internship.strip())

       if has_project and has_internship and score >= 60:
         decision = "Shortlisted (After Review) "
       else:
         decision = "Rejected (After Review) "

    return Response({
        "resume_id": resume.id,
        "decision": decision
    })
        
class AllProfilesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # 👤 Jobseeker → only own resume
        if request.user.role == 'jobseeker':
            resumes = Resume.objects.filter(user=request.user)
        else:
            # 🏢 Recruiter → all resumes
            resumes = Resume.objects.all()

        job = Job.objects.first()
        if not job:
            return Response({"error": "No job found"}, status=404)

        results = []

        for resume in resumes:

            resume_skills = [s.strip().lower() for s in resume.skills.split(",") if s.strip()] if resume.skills else []
            job_skills = [s.strip().lower() for s in job.required_skills.split(",") if s.strip()]
            matched = list(set(resume_skills) & set(job_skills))
            
            score = round((len(matched) / len(resume_skills)) * 100) if resume_skills else 0

            if score < 40:
                level = "Low"
            elif score <= 70:
                level = "Average"
            else:
                level = "High"

            # 🎯 Decision
            if score < 40:
             decision = "Rejected ❌"

            elif score > 70:
               decision = "Shortlisted ✅"

            else:
               has_project = bool(resume.projects and resume.projects.strip())
               has_internship = bool(resume.internship and resume.internship.strip())

               if has_project and has_internship:
                  decision = "Shortlisted (After Review) ⚠️"
               else:
                   decision = "Rejected (After Review) ❌"

            # =========================
            # 👤 JOBSEEKER VIEW
            # =========================
            if request.user.role == 'jobseeker':

                if level == "Average":
                    status = "Profile under review"
                else:
                    status = decision

                if request.user.role == 'jobseeker':

                 results.append({
                        "resume_id": resume.id,
                        "status": decision   # 🔥 direct decision
                    })
            # =========================
            # 🏢 RECRUITER VIEW
            # =========================
            else:
                results.append({
                    "resume_id": resume.id,
                    "user": resume.user.username,
                    "score": score,
                    "level": level,
                    "decision": decision,
                    "status": "Review Required" if level == "Average" else "Auto Decision"
                })

        return Response(results)
    
class AllResultsView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):

        if request.user.role != 'recruiter':
            return Response({"error": "Only recruiters allowed"}, status=403)
    
        resumes = Resume.objects.all()
        job = Job.objects.get(id=job_id)

        job_skills = [s.strip().lower() for s in job.required_skills.split(",")]

        results = []

        for resume in resumes:
            resume_skills = [s.strip().lower() for s in resume.skills.split(",")] if resume.skills else []

            matched = list(set(resume_skills) & set(job_skills))

            if job_skills:
                score = round((len(matched) / len(job_skills)) * 100)
            else:
                score = 0

            # decision
            if score < 40:
                decision = "Rejected "
            elif score == 40:
               decision = "Rejected (After Review)"
            elif score > 70:
                decision = "Shortlisted (After Review)"
            else:
                decision = "Shortlisted "

            results.append({
                "resume_id": resume.id,
                "score": score,
                "decision": decision
            })

        return Response(results)
class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        resumes = Resume.objects.filter(user=request.user)
        job = Job.objects.first()

        results = []

        for resume in resumes:

            resume_skills = [s.strip().lower() for s in resume.skills.split(",")] if resume.skills else []
            job_skills = [s.strip().lower() for s in job.required_skills.split(",")]

            matched = list(set(resume_skills) & set(job_skills))
            score = round((len(matched) / len(job_skills)) * 100) if job_skills else 0

            if score < 40:
                decision = "Rejected "
            elif score > 70:
                decision = "Shortlisted "
            else:
                decision = "Shortlisted (After Review) "

            results.append({
                   "resume_id": resume.id,
                    "user": resume.user.username,
                   "skills": resume.skills,
                "projects": resume.projects,
                "internship": resume.internship,
                "decision": decision
            })

        return Response(results)