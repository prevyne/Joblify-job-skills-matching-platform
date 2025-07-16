from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from .models import UserProfile, JobApplication
from .forms import SignUpForm, UserProfileEditForm
from jobs.models import JobPosting

def signup(request):
    """Handles the signup process for new job seekers."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                group = Group.objects.get(name='JobSeekers')
                user.groups.add(group)
            except Group.DoesNotExist:
                messages.error(request, "Configuration error: 'JobSeekers' group not found.")
            
            UserProfile.objects.create(user=user)
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile_detail(request):
    """Displays the logged-in user's own profile page."""
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'profiles/profile_detail.html', {'profile': profile})

@login_required
def profile_edit(request):
    """Handles editing for the logged-in user's profile."""
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profiles:profile_detail')
    else:
        form = UserProfileEditForm(instance=profile)
    
    return render(request, 'profiles/profile_edit.html', {'form': form, 'profile': profile})

@login_required
def applicant_profile_detail(request, pk):
    """Displays a specific applicant's profile, for an employer to view."""
    profile = get_object_or_404(UserProfile, pk=pk)
    return render(request, 'profiles/applicant_profile_display.html', {'profile': profile})

@login_required
def my_applications(request):
    """Shows a paginated list of the user's job applications."""
    application_list = JobApplication.objects.filter(user_profile__user=request.user).order_by('-application_date')
    paginator = Paginator(application_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'profiles/my_applications.html', {'applications': page_obj})

@login_required
def apply_for_job(request, job_pk):
    """
    Handles the logic for a user applying to a job.
    Correctly handles new applications and re-applications.
    """
    job_posting = get_object_or_404(JobPosting, pk=job_pk, is_active=True)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    existing_application = JobApplication.objects.filter(user_profile=user_profile, job_posting=job_posting).first()

    # Prevent applying if an active application already exists
    if existing_application and existing_application.status not in ['withdrawn_by_applicant', 'rejected_by_employer']:
        messages.warning(request, 'You have an active application for this job.')
        return redirect('jobs:job_detail', pk=job_pk)

    if request.method == 'POST':
        # If re-applying, update the existing application
        if existing_application:
            existing_application.status = 'submitted'
            existing_application.application_date = timezone.now() # Update the date
            existing_application.save()
            messages.success(request, f'You have successfully re-applied for "{job_posting.title}".')
        # Otherwise, create a new application
        else:
            JobApplication.objects.create(user_profile=user_profile, job_posting=job_posting)
            messages.success(request, f'Your application for "{job_posting.title}" has been submitted!')
        
        return redirect('profiles:my_applications')
    
    return redirect('jobs:job_detail', pk=job_pk)

@login_required
def withdraw_application(request, application_pk):
    """Allows a user to withdraw their job application."""
    application = get_object_or_404(JobApplication, pk=application_pk, user_profile__user=request.user)
    if request.method == 'POST':
        application.status = 'withdrawn_by_applicant'
        application.save()
        messages.success(request, 'You have successfully withdrawn your application.')
        return redirect('profiles:my_applications')
    return redirect('profiles:my_applications')

@login_required
def login_redirect_view(request):
    """Redirects users to the appropriate dashboard after login."""
    if request.user.groups.filter(name='Employers').exists():
        return redirect('employers:employer_dashboard')
    elif request.user.groups.filter(name='JobSeekers').exists():
        return redirect('jobs:job_list')
    else:
        return redirect('admin:index')
