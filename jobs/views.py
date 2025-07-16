from django.shortcuts import render, get_object_or_404
from .models import JobPosting 
from django.db.models import Q
from profiles.models import UserProfile, JobApplication
from django.shortcuts import render

#View to list all active job postings
def job_list(request):
    active_jobs=JobPosting.objects.filter(is_active=True)
    query = request.GET.get('q') # Get the search query from the URL parameter 'q'

    if query:
        active_jobs = active_jobs.filter(
            Q(title__icontains=query) | 
            Q(company__name__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) | 
            Q(skills_required__name__icontains=query) 
        ).distinct() # Use distinct() because searching across ManyToManyField (skills) can cause duplicates

    #Creating a context dictionary to pass data to the template
    context={
        'jobs': active_jobs,
    }
    # Render the HTML template 'jobs/jobposting_list.html' with the context data
    return render(request, 'jobs/jobposting_list.html', context)

#View to display the details of a single job posting
def job_detail(request, pk):
    job = get_object_or_404(JobPosting, pk=pk, is_active=True)
    
    user_can_apply = False
    already_applied = False # Default to False
    is_job_seeker = False
    application_is_active = False # Flag to indicate if an existing application is in an "active" state

    if request.user.is_authenticated:
        try:
            user_profile = request.user.profile # Assuming related_name is 'profile'
            if request.user.groups.filter(name='JobSeekers').exists():
                is_job_seeker = True
                
                # Check for an existing application
                existing_application = JobApplication.objects.filter(
                    user_profile=user_profile, 
                    job_posting=job
                ).first()

                if existing_application:
                    # Define statuses that prevent re-application
                    active_application_statuses = [
                        'submitted', 'viewed', 'shortlisted', 
                        'interviewing', 'offered', 'hired'
                    ]
                    if existing_application.status in active_application_statuses:
                        already_applied = True # User has an active application
                        application_is_active = True 
                    # If status is 'withdrawn_by_applicant' or 'rejected_by_employer',
                    # already_applied remains False, allowing re-application.
            
                # User can apply if they are a job seeker and don't have an active application
                if is_job_seeker and not already_applied:
                    user_can_apply = True
                    
        except UserProfile.DoesNotExist:
            # User is authenticated but has no UserProfile, so cannot be a job seeker here
            is_job_seeker = False
            # user_can_apply and already_applied remain False

    context = {
        'job': job,
        'user_can_apply': user_can_apply,
        'already_applied': already_applied, # This will be True only if an *active* application exists
        'is_job_seeker': is_job_seeker,
        'application_is_active': application_is_active,
    }
    
    return render(request, 'jobs/jobposting_detail.html', context)

def home(request):
    """
    View for the site's landing page.
    """
    return render(request, 'jobs/home.html')
