from django.urls import path
from . import views # I'll create the signup view next

app_name = 'profiles'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('me/', views.profile_view, name='profile_view'),
    path('me/edit/', views.profile_edit, name='profile_edit'),
    path('login_redirect/', views.login_redirect_view, name='login_redirect'),
    path('apply/<int:job_pk>/', views.apply_for_job, name='apply_for_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('applicant/<str:username>/', views.applicant_profile_detail, name='applicant_profile_detail'),
    path('application/<int:application_pk>/withdraw/', views.withdraw_application, name='withdraw_application'),
]