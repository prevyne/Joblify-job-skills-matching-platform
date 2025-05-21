from django.contrib import admin
from .models import Company, JobPosting #import my models

# Register my models here.
admin.site.register(Company)
admin.site.register(JobPosting)