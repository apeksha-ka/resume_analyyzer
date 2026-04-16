from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer
from .models import User
from django.contrib.auth import authenticate

class RegisterView(APIView):
    def post(self, request):

        user = User.objects.create_user(
            username=request.data['username'],
            password=request.data['password'],
            email=request.data['email'],
            role=request.data['role']
        )

        return Response({"message": "User registered successfully"})
    
class LoginView(APIView):
    def post(self, request):

        user = authenticate(
            username=request.data['username'],
            password=request.data['password']
        )

        if user:
            return Response({
                "message": "Login success",
                "role": user.role
            })
        else:
            return Response({"error": "Invalid credentials"})
