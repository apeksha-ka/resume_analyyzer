from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Resume
from .serializers import ResumeSerializer

class UploadResumeView(APIView):
       permission_classes = [IsAuthenticated]

       def post(self, request):   # ✅ inside class
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"msg": "Resume uploaded"})
        return Response(serializer.errors)
