from rest_framework.views import APIView
from rest_framework.response import Response
from resumes.models import Resume
from .models import Job
import re

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
        

        # clean resume
        resume_text = resume.extracted_text.lower()
        resume_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', resume_text)
        resume_words = set(resume_text.split())

        # clean job skills
        job_skills = [s.strip().lower() for s in job.required_skills.split(',')]

        matched = []

        # ✅ CORRECT LOOP
        for skill in job_skills:
            skill_words = skill.split()

            if any(f" {word} " in f" {resume_text} " for word in skill_words):
                matched.append(skill)
                continue

            # synonym match
            if skill in SYNONYMS:
                for alt in SYNONYMS[skill]:
                    if alt in resume_text:
                        matched.append(skill)
                        break
                matched = list(set(matched))

        # score
        if job_skills:
            score = (len(matched) / len(job_skills)) * 100
        else:
            score = 0

        return Response({
            "matched_skills": matched,
            "score": score
        })