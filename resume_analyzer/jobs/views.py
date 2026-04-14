from rest_framework.views import APIView
from rest_framework.response import Response
from resumes.models import Resume
from .models import Job
import re
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

SYNONYMS = {
    "ml": ["machine learning"],
    "nlp": ["natural language processing"],
    "js": ["javascript"]
}


class MatchJobView(APIView):
    def get(self, request, resume_id, job_id):

        print("API HIT")

        resume = Resume.objects.get(id=resume_id)
        job = Job.objects.get(id=job_id)

        resume_skills = [s.strip().lower() for s in resume.skills.split(",")] if resume.skills else []
        job_skills = [s.strip().lower() for s in job.required_skills.split(",")]

        matched = list(set(resume_skills) & set(job_skills))
        # score
        if job_skills:
            score = round((len(matched) / len(job_skills)) * 100, 2)
        else:
           score = 0
        if score < 40:
          level = "Low"
          decision = "Rejected ❌"
        elif score <= 70:
           level = "Average"
           decision = "Review Required ⚠️"
        else:
           level = "High"
           decision = "Shortlisted ✅"

        return Response({
            "matched_skills": matched,
            "score": score,
            "level":level,
            "decision" : decision,
        })
class ReviewCheckView(APIView):
    def get(self, request, resume_id):

        resume = Resume.objects.get(id=resume_id)

        
        has_project = bool(resume.projects.strip()) if resume.projects else False

       
        has_internship = bool(resume.internship.strip()) if resume.internship else False

        
        if has_project and has_internship:
            review = "Strong Candidate ✅"
        elif has_project or has_internship:
            review = "Average Candidate ⚠️"
        else:
            review = "Weak Candidate ❌"

        return Response({
            "projects": resume.projects,
            "internship": resume.internship,
            "review": review
        })
    
class AdvancedReviewView(APIView):
    def get(self, request, resume_id):

        resume = Resume.objects.get(id=resume_id)

        
        if resume.projects and "django" in resume.projects.lower():
            skill_depth = "Strong ✅"
        else:
            skill_depth = "Basic ⚠️"

       
        if len(resume.extracted_text) > 500:
            quality = "Good ✅"
        else:
            quality = "Poor ❌"

        
        extras = []
        if resume.certifications:
            extras.append("Certifications ✅")
        if resume.github:
            extras.append("GitHub ✅")

        return Response({
            "skill_depth": skill_depth,
            "resume_quality": quality,
            "extras": extras if extras else "No extras ❌"
        })
class FinalDecisionView(APIView):
    def get(self, request, resume_id, job_id):

        resume = Resume.objects.get(id=resume_id)
        job = Job.objects.get(id=job_id)

        # skills
        resume_skills = [s.strip().lower() for s in resume.skills.split(",")] if resume.skills else []
        job_skills = [s.strip().lower() for s in job.required_skills.split(",")]

        matched = list(set(resume_skills) & set(job_skills))

        # score
        score = round((len(matched) / len(job_skills)) * 100) if job_skills else 0

        # level
        if score < 40:
            level = "Low"
        elif score <= 70:
            level = "Average"
        else:
            level = "High"

        # review (projects + internship)
        # weak check
        weak_project = "basic" in resume.projects.lower() if resume.projects else True
        weak_internship = "workshop" in resume.internship.lower() if resume.internship else True

# final decision
        if score < 40:
          decision = "Rejected "

        elif level == "High" and not weak_project:
             decision = "Shortlisted ✅"

        elif level == "Average":
             if weak_project and weak_internship:
                decision = "Rejected "   
             else:
                decision = "Shortlisted (After Review) ⚠️"

        else:
            decision = "Rejected "

        return Response({
            "score": score,
            "level": level,
            "decision": decision
        })
class AllProfilesView(APIView):
    def get(self, request):

        resumes = Resume.objects.all()
        job = Job.objects.first()   

        results = []

        for resume in resumes:

            resume_skills = [s.strip().lower() for s in resume.skills.split(",")] if resume.skills else []
            job_skills = [s.strip().lower() for s in job.required_skills.split(",")]

            matched = list(set(resume_skills) & set(job_skills))

            score = round((len(matched) / len(job_skills)) * 100) if job_skills else 0

            
            if score < 40:
                level = "Low"
            elif score <= 70:
                level = "Average"
            else:
                level = "High"

            
            weak_project = "basic" in resume.projects.lower() if resume.projects else True
            weak_internship = "workshop" in resume.internship.lower() if resume.internship else True

            
            if score < 40:
               decision = "Rejected "
               review_note = "Low score"

            elif level == "High":
                decision = "Shortlisted ✅"
                review_note = "High score, directly shortlisted"

            elif level == "Average":
                 if weak_project and weak_internship:
                   decision = "Rejected "
                   review_note = "Weak project,internship and no certification and github"
                 else:
                    decision = "Shortlisted (After Review) ⚠️"
                    review_note = "Has some project or internship, needs manual review"

            else:
                decision = "Rejected "
                review_note = "Not suitable"

            if score > 70:
              message = "Strong candidate for this role"
            elif score >= 40:
              message = "Needs improvement"
            else:
             message = "Not suitable"
            results.append({
                "resume_id": resume.id,
                "score": score,
                "level": level,
                "decision": decision,
                "review_note": review_note if level == "Average" else "Direct decision",
                "message":message
            })

        return Response(results)
    
class AllResultsView(APIView):
    def get(self, request, job_id):
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
                decision = "Rejected ❌"
            elif score == 40:
               decision = "Rejected (After Review)"
            elif score > 70:
                decision = "Shortlisted (After Review)"
            else:
                decision = "Shortlisted ✅"

            results.append({
                "resume_id": resume.id,
                "score": score,
                "decision": decision
            })

        return Response(results)