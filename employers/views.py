from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from .forms import EmployerSignUpForm
from jobs.models import Company, JobPosting # Import JobPosting
from .models import EmployerProfile
from .forms import EmployerSignUpForm, JobPostingForm
from django.views.decorators.http import require_POST # To ensure this view only accepts POST requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmployerSignUpForm, JobPostingForm, CompanyEditForm
from profiles.models import JobApplication, UserProfile
from django.conf import settings
from django.core.mail import send_mail

def employer_signup(request):
    if request.method == 'POST':
        form = EmployerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            #Add the new user to the 'Employers' group
            try:
                employers_group = Group.objects.get(name='Employers')
                user.groups.add(employers_group)
            except Group.DoesNotExist:
                # Fallback: This should ideally not happen if groups were created
                messages.error(request, "Configuration error: 'Employers' group not found. Please contact support.")
                print("CRITICAL: 'Employers' group not found during employer signup.")

            company_name = form.cleaned_data.get('company_name')
            company_website = form.cleaned_data.get('company_website')
            
            company, created = Company.objects.get_or_create(
                name__iexact=company_name, # Case-insensitive match for existing company
                defaults={'name': company_name, 'website': company_website} # Values if creating new
            )
            
            if not created and company_website and not company.website:
                # If company existed but had no website, update it with the provided one
                company.website = company_website
                company.save()
            elif created:
                messages.success(request, f"Company profile for '{company.name}' created.")

            EmployerProfile.objects.create(
                user=user,
                company=company,
            )

            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your employer account has been created.")
            
            return redirect('employers:employer_dashboard') 
        else:
            messages.error(request, "Please correct the errors below.")
            
    else: # For GET requests
        form = EmployerSignUpForm()
        
    return render(request, 'employers/signup_employer.html', {'form': form})

#Employer Dashboard view
@login_required
def employer_dashboard(request):
    try:
        employer_profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        # If a user does not have an employer profile,Redirect them or show an error.
        messages.error(request, "You do not have an employer profile. Please contact support if this is an error.")
        return redirect('jobs:job_list') # Or to a generic homepage

    company = employer_profile.company
    
    # Fetch job postings by this employer's company
    posted_jobs = JobPosting.objects.filter(company=company).order_by('-date_posted')
    active_jobs_count = posted_jobs.filter(is_active=True).count()
    inactive_jobs_count = posted_jobs.filter(is_active=False).count()


    context = {
        'employer_profile': employer_profile,
        'company': company,
        'posted_jobs': posted_jobs,
        'active_jobs_count': active_jobs_count,
        'inactive_jobs_count': inactive_jobs_count,
        'total_jobs_count': posted_jobs.count(),
    }
    return render(request, 'employers/dashboard.html', context)

#Create Job Posting
@login_required
def create_job_posting(request):
    # Ensure the user is an employer and has an associated company
    try:
        employer_profile = request.user.employer_profile
        company = employer_profile.company
    except EmployerProfile.DoesNotExist:
        messages.error(request, "You must have an employer profile and be associated with a company to post a job.")
        return redirect('employers:employer_dashboard') # Or a more appropriate page

    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.company = company # Assign the employer's company
            job_posting.save() # Now save the JobPosting instance to the database

            messages.success(request, f"Job posting '{job_posting.title}' created successfully!")
            return redirect('employers:employer_dashboard') 
        else:
            messages.error(request, "Please correct the errors below.")
    else: # For GET requests
        form = JobPostingForm()

    context = {
        'form': form,
        'company_name': company.name,
    }
    return render(request, 'employers/create_job_posting.html', context)

#Edit Job posting View
@login_required
def edit_job_posting(request, job_pk):
    # Fetch the specific job posting to be edited
    job_to_edit = get_object_or_404(JobPosting, pk=job_pk)

    # Authorization check: Ensure the logged-in employer's company owns this job posting
    try:
        employer_profile = request.user.employer_profile
        if job_to_edit.company != employer_profile.company:
            messages.error(request, "You are not authorized to edit this job posting.")
            # Or raise HttpResponseForbidden("You are not authorized to edit this job posting.")
            return redirect('employers:employer_dashboard')
    except EmployerProfile.DoesNotExist:
        messages.error(request, "You must have an employer profile to edit job postings.")
        return redirect('employers:employer_dashboard')

    if request.method == 'POST':
        # Populate the form with submitted data AND the instance to be updated
        form = JobPostingForm(request.POST, instance=job_to_edit)
        if form.is_valid():
            updated_job = form.save() # Save the changes to the JobPosting instance
            messages.success(request, f"Job posting '{updated_job.title}' updated successfully!")
            return redirect('employers:employer_dashboard') # Or to job_detail page: redirect('jobs:job_detail', pk=updated_job.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else: # For GET requests
        # Display the form pre-filled with the job's current data
        form = JobPostingForm(instance=job_to_edit)

    context = {
        'form': form,
        'job_to_edit': job_to_edit, # Pass the job instance for context (e.g., display title)
        'company_name': job_to_edit.company.name, # For consistency with create_job_posting template if reusing
        'is_editing': True # Flag to differentiate from create view in template if reusing
    }
    return render(request, 'employers/create_job_posting.html', context)

#Toggle job status View
@login_required
@require_POST # This decorator ensures that this view can only be accessed via a POST request
def toggle_job_status(request, job_pk):
    """
    Toggles the 'is_active' status of a job posting.
    Only callable via POST request by the employer who owns the job.
    """
    # Fetch the specific job posting
    job_to_toggle = get_object_or_404(JobPosting, pk=job_pk)

    # Authorization check: Ensure the logged-in employer's company owns this job posting
    try:
        employer_profile = request.user.employer_profile
        if job_to_toggle.company != employer_profile.company:
            messages.error(request, "You are not authorized to change the status of this job posting.")
            # Or return HttpResponseForbidden("You are not authorized to change the status of this job posting.")
            return redirect('employers:employer_dashboard')
    except EmployerProfile.DoesNotExist:
        messages.error(request, "You must have an employer profile to manage job postings.")
        return redirect('employers:employer_dashboard')

    # Toggle the is_active status
    job_to_toggle.is_active = not job_to_toggle.is_active
    job_to_toggle.save()

    if job_to_toggle.is_active:
        messages.success(request, f"Job posting '{job_to_toggle.title}' has been activated.")
    else:
        messages.success(request, f"Job posting '{job_to_toggle.title}' has been deactivated.")
    
    return redirect('employers:employer_dashboard')

#Manage jobs list
@login_required
def manage_jobs_list(request):
    """
    Displays a paginated list of all job postings for the logged-in employer's company.
    """
    # Ensure the user is an employer and has an associated company
    try:
        employer_profile = request.user.employer_profile
        company = employer_profile.company
    except EmployerProfile.DoesNotExist:
        messages.error(request, "You must have an employer profile to manage job postings.")
        return redirect('employers:employer_dashboard') # Or a more appropriate page

    # Fetch all job postings by this employer's company, ordered by most recent
    all_posted_jobs_list = JobPosting.objects.filter(company=company).order_by('-date_posted')

    # Pagination
    paginator = Paginator(all_posted_jobs_list, 10) # Show 10 jobs per page
    page_number = request.GET.get('page')
    try:
        paginated_jobs = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_jobs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_jobs = paginator.page(paginator.num_pages)

    context = {
        'company': company,
        'posted_jobs': paginated_jobs, # Pass the paginated list of jobs
        'is_paginated': paginated_jobs.has_other_pages(), # Boolean to check if pagination is needed
    }
    return render(request, 'employers/manage_jobs_list.html', context)

#Company Profile view
@login_required
def edit_company_profile(request):
    """
    Allows an authenticated employer to edit their associated company's profile.
    """
    try:
        employer_profile = request.user.employer_profile
        company_to_edit = employer_profile.company
    except EmployerProfile.DoesNotExist:
        messages.error(request, "You must have an employer profile to edit company details.")
        return redirect('jobs:job_list')
    except Company.DoesNotExist:
        messages.error(request, "Associated company not found. Please contact support.")
        return redirect('employers:employer_dashboard')

    if request.method == 'POST':
        form = CompanyEditForm(request.POST, request.FILES, instance=company_to_edit)
        if form.is_valid():
            updated_company = form.save()
            messages.success(request, f"Company profile for '{updated_company.name}' updated successfully!")
            return redirect('employers:employer_dashboard') # Redirect to employer dashboard
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Display the form pre-filled with the company's current data
        form = CompanyEditForm(instance=company_to_edit)

    context = {
        'form': form,
        'company': company_to_edit, # Pass the company instance for context
    }
    return render(request, 'employers/edit_company_profile.html', context)

#View Applicatns view
@login_required
def view_job_applicants(request, job_pk):
    """
    Displays a list of applicants for a specific job posting,
    with sorting and filtering capabilities.
    """
    job_posting = get_object_or_404(JobPosting, pk=job_pk)

    # Authorization check
    try:
        employer_profile = request.user.employer_profile
        if job_posting.company != employer_profile.company:
            messages.error(request, "You are not authorized to view applicants for this job posting.")
            return redirect('employers:employer_dashboard')
    except EmployerProfile.DoesNotExist:
        messages.error(request, "You must have an employer profile to view job applicants.")
        return redirect('employers:employer_dashboard')

    # Base queryset for applications
    application_list = JobApplication.objects.filter(job_posting=job_posting)\
                                             .select_related('user_profile__user')

    # Get filter and sort parameters from GET request
    filter_status = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '-application_date') # Default sort: newest applications first

    # Apply filtering by status
    if filter_status:
        application_list = application_list.filter(status=filter_status)

    # Apply sorting
    # Validate sort_by parameter to prevent arbitrary ordering
    valid_sort_fields = {
        'application_date': 'application_date',
        '-application_date': '-application_date',
        'user_profile__user__username': 'user_profile__user__username',
        '-user_profile__user__username': '-user_profile__user__username',
        'status': 'status', # Allow sorting by status
        '-status': '-status',
    }
    if sort_by in valid_sort_fields:
        application_list = application_list.order_by(valid_sort_fields[sort_by])
    else:
        # Default or fallback sort if an invalid parameter is given
        application_list = application_list.order_by('-application_date')


    # Pagination
    paginator = Paginator(application_list, 10) # Show 10 applicants per page
    page_number = request.GET.get('page')
    try:
        paginated_applicants = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_applicants = paginator.page(1)
    except EmptyPage:
        paginated_applicants = paginator.page(paginator.num_pages)

    context = {
        'job_posting': job_posting,
        'applicants': paginated_applicants,
        'is_paginated': paginated_applicants.has_other_pages(),
        'available_statuses': JobApplication.STATUS_CHOICES, # Pass status choices to the template
        'current_filter_status': filter_status, # Pass current filter back for form pre-selection
        'current_sort_by': sort_by, # Pass current sort back for form pre-selection
    }
    return render(request, 'employers/view_job_applicants.html', context)

#Update application status
@login_required # type: ignore
@require_POST # This action should only be done via a POST request # type: ignore
def update_application_status(request, application_pk): #
    """
    Updates the status of a specific job application.
    Only callable via POST by an authorized employer.
    """
    application = get_object_or_404(JobApplication, pk=application_pk) # type: ignore #
    job_posting = application.job_posting # Get the related job posting #

    # Authorization check: Ensure the logged-in employer's company owns this job posting
    try:
        employer_profile = request.user.employer_profile # type: ignore #
        if job_posting.company != employer_profile.company: #
            messages.error(request, "You are not authorized to update the status for this application.") # type: ignore #
            return redirect('employers:view_job_applicants', job_pk=job_posting.pk) #
    except EmployerProfile.DoesNotExist: # type: ignore #
        messages.error(request, "You must have an employer profile to manage applications.") # type: ignore #
        return redirect('employers:employer_dashboard') #

    new_status = request.POST.get('new_status') #

    # Validate that the new_status is a valid choice
    valid_statuses = [status_value for status_value, status_display in JobApplication.STATUS_CHOICES] # type: ignore #
    if new_status in valid_statuses: #
        old_status_display = application.get_status_display() # Get status before changing
        application.status = new_status #
        application.save() #
        
        new_status_display = application.get_status_display() # Get new status display name
        
        # Prepare and send email notification to the applicant
        if application.user_profile and application.user_profile.user:
            applicant_user = application.user_profile.user
            job_title = job_posting.title
            company_name = job_posting.company.name if job_posting.company else "our company"
            user_name = applicant_user.first_name if applicant_user.first_name else applicant_user.username
            
            email_subject = f"Update on your application for {job_title}"
            email_body = f"""Dear {user_name},

The status of your application for the position of "{job_title}" at {company_name} has been updated from '{old_status_display}' to '{new_status_display}'.

You can view your application and any further details on your Joblify dashboard.

Best regards,
The Joblify Team"""

            try:
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL, # type: ignore
                    [applicant_user.email],
                    fail_silently=False # Good for development
                )
                messages.success(request, f"Application status for '{applicant_user.username}' updated to '{new_status_display}'. Applicant notified by email.") # type: ignore
            except Exception as e:
                print(f"Error sending status update email to {applicant_user.email}: {e}")
                messages.success(request, f"Application status for '{applicant_user.username}' updated to '{new_status_display}'. Failed to send notification email.") # type: ignore
        else:
            # This case should ideally not happen if data integrity is maintained
            messages.success(request, f"Application status updated to '{new_status_display}', but applicant details are missing for email notification.") # type: ignore

    else:
        messages.error(request, f"Invalid status '{new_status}' selected.") # type: ignore #

    return redirect('employers:view_job_applicants', job_pk=job_posting.pk) 