from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.conf import settings
from django.core.mail import send_mail

from jobs.models import Company, JobPosting
from jobs.services import calculate_similarity
from profiles.models import JobApplication
from .models import EmployerProfile
from .forms import EmployerSignUpForm, JobPostingForm, CompanyEditForm

def employer_signup(request):
    """Handles the signup process for new employers."""
    if request.method == 'POST':
        form = EmployerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                employers_group = Group.objects.get(name='Employers')
                user.groups.add(employers_group)
            except Group.DoesNotExist:
                # This fallback is a safety net for configuration errors.
                messages.error(request, "Configuration error: 'Employers' group not found.")
                print("CRITICAL: 'Employers' group not found during employer signup.")

            company_name = form.cleaned_data.get('company_name')
            company_website = form.cleaned_data.get('company_website')
            company, created = Company.objects.get_or_create(
                name__iexact=company_name,
                defaults={'name': company_name, 'website': company_website}
            )
            if created:
                messages.success(request, f"Company profile for '{company.name}' created.")

            EmployerProfile.objects.create(user=user, company=company)
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your employer account is ready.")
            return redirect('employers:employer_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EmployerSignUpForm()
    return render(request, 'employers/signup_employer.html', {'form': form})

@login_required
def employer_dashboard(request):
    """Displays the main dashboard for the logged-in employer."""
    try:
        employer_profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        messages.error(request, "You do not have an employer profile.")
        return redirect('home')

    company = employer_profile.company
    posted_jobs = JobPosting.objects.filter(company=company).order_by('-date_posted')
    
    context = {
        'employer_profile': employer_profile,
        'company': company,
        'posted_jobs': posted_jobs,
        'active_jobs_count': posted_jobs.filter(is_active=True).count(),
        'inactive_jobs_count': posted_jobs.filter(is_active=False).count(),
        'total_jobs_count': posted_jobs.count(),
    }
    return render(request, 'employers/dashboard.html', context)

@login_required
def create_job_posting(request):
    """Handles the creation of a new job posting."""
    try:
        company = request.user.employer_profile.company
    except EmployerProfile.DoesNotExist:
        messages.error(request, "You must have an employer profile to post a job.")
        return redirect('employers:employer_dashboard')

    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.company = company
            job_posting.posted_by = request.user
            job_posting.save()
            form.save_m2m() # Important for saving ManyToMany fields like skills
            messages.success(request, f"Job posting '{job_posting.title}' created successfully!")
            return redirect('employers:employer_dashboard')
    else:
        form = JobPostingForm()
    return render(request, 'employers/create_job_posting.html', {'form': form})

@login_required
def edit_job_posting(request, job_pk):
    """Handles editing an existing job posting."""
    job_to_edit = get_object_or_404(JobPosting, pk=job_pk)
    if job_to_edit.company != request.user.employer_profile.company:
        messages.error(request, "You are not authorized to edit this job posting.")
        return redirect('employers:employer_dashboard')

    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job posting '{job_to_edit.title}' updated successfully!")
            return redirect('employers:manage_jobs_list')
    else:
        form = JobPostingForm(instance=job_to_edit)
    return render(request, 'employers/edit_job_posting.html', {'form': form, 'job': job_to_edit})

@login_required
@require_POST
def toggle_job_status(request, job_pk):
    """Toggles the 'is_active' status of a job posting."""
    job = get_object_or_404(JobPosting, pk=job_pk)
    if job.company != request.user.employer_profile.company:
        messages.error(request, "You are not authorized to modify this job posting.")
        return redirect('employers:manage_jobs_list')

    job.is_active = not job.is_active
    job.save()
    status = "activated" if job.is_active else "deactivated"
    messages.success(request, f"Job posting '{job.title}' has been {status}.")
    return redirect('employers:manage_jobs_list')

@login_required
def manage_jobs_list(request):
    """Displays a paginated list of all job postings for the employer's company."""
    try:
        company = request.user.employer_profile.company
    except EmployerProfile.DoesNotExist:
        messages.error(request, "You must have an employer profile to manage jobs.")
        return redirect('home')

    jobs_list = JobPosting.objects.filter(company=company).order_by('-date_posted')
    paginator = Paginator(jobs_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'employers/manage_jobs_list.html', {'posted_jobs': page_obj})

@login_required
def edit_company_profile(request):
    """Allows an employer to edit their associated company's profile."""
    company_to_edit = request.user.employer_profile.company
    if request.method == 'POST':
        form = CompanyEditForm(request.POST, request.FILES, instance=company_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, "Company profile updated successfully!")
            return redirect('employers:employer_dashboard')
    else:
        form = CompanyEditForm(instance=company_to_edit)
    return render(request, 'employers/edit_company_profile.html', {'form': form})

@login_required
def view_job_applicants(request, job_pk):
    """Displays applicants for a job, sorted by an AI-calculated match score."""
    job_posting = get_object_or_404(JobPosting, pk=job_pk)
    if job_posting.company != request.user.employer_profile.company:
        messages.error(request, "You are not authorized to view these applicants.")
        return redirect('employers:manage_jobs_list')

    application_list = JobApplication.objects.filter(job_posting=job_posting).select_related('user_profile__user')

    # Calculate match score for each applicant based on their profile vs the job description.
    job_skills = ' '.join([s.name for s in job_posting.skills_required.all()])
    job_text = f"{job_posting.title} {job_posting.description} {job_skills}"

    for application in application_list:
        profile = application.user_profile
        profile_skills = ' '.join([s.name for s in profile.skills.all()])
        profile_text = f"{profile.bio} {profile_skills}"
        score = calculate_similarity(job_text, profile_text)
        application.match_score = int(score * 100)

    # Sort applicants by match score (highest first).
    application_list_sorted = sorted(list(application_list), key=lambda app: app.match_score, reverse=True)

    # Allow optional filtering by status on the AI-sorted list.
    filter_status = request.GET.get('status', '')
    if filter_status:
        application_list_sorted = [app for app in application_list_sorted if app.status == filter_status]

    paginator = Paginator(application_list_sorted, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'job_posting': job_posting,
        'applicants': page_obj,
        'available_statuses': JobApplication.STATUS_CHOICES,
        'current_filter_status': filter_status,
    }
    return render(request, 'employers/view_job_applicants.html', context)

@login_required
@require_POST
def update_application_status(request, application_pk):
    """Updates the status of a job application and notifies the applicant."""
    application = get_object_or_404(JobApplication, pk=application_pk)
    if application.job_posting.company != request.user.employer_profile.company:
        messages.error(request, "You are not authorized to update this application.")
        return redirect('employers:manage_jobs_list')

    new_status = request.POST.get('new_status')
    valid_statuses = [choice[0] for choice in JobApplication.STATUS_CHOICES]
    if new_status in valid_statuses:
        old_status_display = application.get_status_display()
        application.status = new_status
        application.save()
        new_status_display = application.get_status_display()

        # Notify the applicant via email about the status change.
        applicant_user = application.user_profile.user
        email_subject = f"Update on your application for {application.job_posting.title}"
        email_body = f"Hi {applicant_user.first_name},\n\nThe status of your application for '{application.job_posting.title}' has been updated from '{old_status_display}' to '{new_status_display}'.\n\nBest regards,\nThe Joblify Team"
        
        try:
            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [applicant_user.email], fail_silently=False)
            messages.success(request, f"Application status updated to '{new_status_display}'. Applicant has been notified.")
        except Exception as e:
            print(f"ERROR: Email sending failed - {e}")
            messages.warning(request, f"Application status updated, but failed to send notification email.")
    else:
        messages.error(request, "Invalid status selected.")
    return redirect('employers:view_job_applicants', job_pk=application.job_posting.pk)