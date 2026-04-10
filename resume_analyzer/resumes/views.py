from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Resume
import PyPDF2


# ✅ Extract text from PDF
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


# ✅ Extract skills
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

    return list(set(found_skills))  # remove duplicates


# ✅ Upload Resume API (MULTIPLE FILE SUPPORT)
class UploadResumeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        files = request.FILES.getlist('file')

        if not files:
            return Response({"error": "No file uploaded"})

        results = []

        for file in files:

            # ✅ Allow only PDFs
            if not file.name.endswith('.pdf'):
                results.append({
                    "file": file.name,
                    "error": "Only PDF files allowed"
                })
                continue

            # 🔥 Extract text
            text = extract_text_from_pdf(file)

            # 🔥 Reset file pointer
            file.seek(0)

            # 🔥 Extract skills safely
            skills = extract_skills(text) if text else []

            # 🔥 Save to DB
            resume = Resume.objects.filter(user=request.user).first()

            if resume:
              resume.file = file
              resume.extracted_text = text
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