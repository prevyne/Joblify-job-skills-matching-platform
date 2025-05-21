from django.urls import path
from . import views # I'll create views.py next

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'), # e.g., /jobs/ -> will call job_list view
    path('<int:pk>/', views.job_detail, name='job_detail'), # e.g., /jobs/5/ -> will call job_detail view
]