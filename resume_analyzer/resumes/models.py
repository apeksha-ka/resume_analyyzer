from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    projects = models.TextField(blank=True)
    internship = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    github = models.URLField(blank=True)
