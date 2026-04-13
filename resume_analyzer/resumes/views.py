from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Resume
import PyPDF2
from rest_framework.views import APIView
from rest_framework.response import Response
from resumes.models import Resume




def extract_text_from_pdf(file):
    try:
        pdf = PyPDF2.PdfReader(file)
        text = ""

        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        return text.strip()

    except Exception as e:
        print("PDF ERROR:", e)
        return ""



def extract_skills(text):
    skills_list = [
        'python', 'java', 'django', 'sql', 'html', 'css',
        'react', 'node', 'javascript', 'mongodb',
        'machine learning', 'ml', 'nlp', 'data science'
    ]

    found_skills = []
    text = text.lower()

    for skill in skills_list:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))  



class UploadResumeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        files = request.FILES.getlist('file')

        if not files:
            return Response({"error": "No file uploaded"})

        results = []

        for file in files:

            
            if not file.name.endswith('.pdf'):
                results.append({
                    "file": file.name,
                    "error": "Only PDF files allowed"
                })
                continue
            if Resume.objects.filter(user=request.user, file=file.name).exists():
              results.append({
            "file": file.name,
            "error": "File already uploaded"
            })
              continue

           
            text = extract_text_from_pdf(file)

           
            file.seek(0)

           
            skills = extract_skills(text) if text else []

            
            resume = Resume.objects.filter(user=request.user).first()

            if resume:
              resume.file = file
              resume.extracted_text = text
              resume.skills = ",".join(skills)
              resume.save()
            else:
               resume = Resume.objects.create(
               user=request.user,
               file=file,
               extracted_text=text
        )
  
            results.append({
                "resume_id": resume.id,
                "skills": skills,
                "text_length": len(text)
            })

        return Response({
            "message": "All resumes uploaded successfully",
            "data": results
        })
   

class UpdateResumeDetails(APIView):
    def post(self, request, resume_id):

        resume = Resume.objects.get(id=resume_id)

        resume.projects = request.data.get("projects", "")
        resume.internship = request.data.get("internship", "")
        resume.certifications = request.data.get("certifications", "")
        resume.github = request.data.get("github", "")
        resume.save()

        return Response({
            "message": "Details updated successfully"
        })