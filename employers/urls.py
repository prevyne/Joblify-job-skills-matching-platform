from django.urls import path
from . import views

app_name = 'employers'

urlpatterns = [
    path('signup/', views.employer_signup, name='signup_employer'),
        # I will add other employer-related URLs here later, e.g., dashboard, post job, etc.
    path('dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('jobs/post/', views.create_job_posting, name='create_job_posting'),
    path('jobs/<int:job_pk>/edit/', views.edit_job_posting, name='edit_job_posting'),
    path('jobs/<int:job_pk>/toggle-status/', views.toggle_job_status, name='toggle_job_status'),
    path('jobs/manage/', views.manage_jobs_list, name='manage_jobs_list'),
    path('company/edit/', views.edit_company_profile, name='edit_company_profile'),
    path('jobs/<int:job_pk>/applicants/', views.view_job_applicants, name='view_job_applicants'),
    path('applications/<int:application_pk>/update-status/', views.update_application_status, name='update_application_status'),
    ]
    