from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import JobPosting
from profiles.models import UserProfile, JobApplication
from .services import calculate_similarity, calculate_experience_score

def job_list(request):
    """
    Lists active job postings, with AI-powered sorting for logged-in job seekers.
    """
    active_jobs = JobPosting.objects.filter(is_active=True).order_by('-date_posted')
    query = request.GET.get('q')

    if query:
        # Preserve existing search functionality
        active_jobs = active_jobs.filter(
            Q(title__icontains=query) |
            Q(company__name__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(skills_required__name__icontains=query)
        ).distinct()

    # AI Matching for logged-in job seekers
    if request.user.is_authenticated:
        try:
            seeker_profile = UserProfile.objects.get(user=request.user)
            profile_skills = ' '.join([skill.name for skill in seeker_profile.skills.all()])
            profile_text = f"{seeker_profile.bio} {profile_skills} {profile_skills} {profile_skills}"

            # Calculate score for each job and sort the list
            if profile_text.strip():
                for job in active_jobs:
                    job_skills = ' '.join([skill.name for skill in job.skills_required.all()])
                    job_text = f"{job.title} {job.description} {job_skills} {job_skills} {job_skills}"
                    
                    # --- START: Updated AI Score Calculation ---
                    text_score = calculate_similarity(profile_text, job_text)
                    exp_score = calculate_experience_score(job.experience_level, seeker_profile.experience_level)

                    # Combine scores with a weighted average
                    final_score = (0.7 * text_score) + (0.3 * exp_score)
                    job.match_score = int(final_score * 100)
                    # --- END: Updated AI Score Calculation ---
                
                active_jobs = sorted(list(active_jobs), key=lambda j: j.match_score, reverse=True)

        except UserProfile.DoesNotExist:
            # User is authenticated but is not a job seeker.
            pass

    context = {
        'jobs': active_jobs,
    }
    return render(request, 'jobs/jobposting_list.html', context)


def job_detail(request, pk):
    """Displays the details of a single job posting."""
    job = get_object_or_404(JobPosting, pk=pk, is_active=True)
    user_can_apply = False
    already_applied = False
    application_is_active = False

    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if request.user.groups.filter(name='JobSeekers').exists():
                existing_application = JobApplication.objects.filter(
                    user_profile=user_profile,
                    job_posting=job
                ).first()

                if existing_application:
                    active_statuses = ['submitted', 'viewed', 'shortlisted', 'interviewing', 'offered', 'hired']
                    if existing_application.status in active_statuses:
                        already_applied = True
                        application_is_active = True
                
                if not already_applied:
                    user_can_apply = True
        except UserProfile.DoesNotExist:
            pass # User is not a job seeker, so flags remain False.

    context = {
        'job': job,
        'user_can_apply': user_can_apply,
        'already_applied': already_applied,
        'application_is_active': application_is_active,
    }
    return render(request, 'jobs/jobposting_detail.html', context)


def home(request):
    """View for the site's landing page."""
    return render(request, 'jobs/home.html')