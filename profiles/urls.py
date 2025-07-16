from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    # User authentication and profile management
    path('signup/', views.signup, name='signup'),
    
    # This now correctly points to the 'profile_detail' view function
    path('me/', views.profile_detail, name='profile_detail'),
    
    path('me/edit/', views.profile_edit, name='profile_edit'),
    
    # Application management for job seekers
    path('apply/<int:job_pk>/', views.apply_for_job, name='apply_for_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:application_pk>/withdraw/', views.withdraw_application, name='withdraw_application'),

    # URL for an employer to view a specific applicant's profile
    path('applicant/<int:pk>/', views.applicant_profile_detail, name='applicant_profile_display'),
    
    # Utility view for redirecting users after login
    path('login_redirect/', views.login_redirect_view, name='login_redirect'),
]
