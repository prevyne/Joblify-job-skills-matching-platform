from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import login_required # Import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignUpForm, UserProfileEditForm 
from .models import UserProfile, User 
from django.contrib.auth.models import Group
from django.views.decorators.http import require_POST
from .models import UserProfile, JobApplication
from jobs.models import JobPosting
from django.db import IntegrityError # To catch unique_together constraint violations
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # For pagination
from django.http import Http404
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from employers.models import EmployerProfile

#Signup View
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save() 
            
            UserProfile.objects.create(user=user)
            
            try:
                job_seekers_group = Group.objects.get(name='JobSeekers')
                user.groups.add(job_seekers_group)
            except Group.DoesNotExist:
                print("Warning: 'JobSeekers' group not found. User was not added to the group.")
                pass 
            
            login(request, user)
            return redirect('jobs:job_list')
    else:
        form = SignUpForm() # Display an empty form for GET requests
        
    return render(request, 'registration/signup.html', {'form': form})

#Profile view
@login_required # Ensures only logged-in users can access this view
def profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    context = {
        'profile': user_profile,
    }
    return render(request, 'profiles/profile_detail.html', context)

#Profile edit view
@login_required # Ensures only logged-in users can access this view
def profile_edit(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save() # Save the changes to the UserProfile instance
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profiles:profile_view')
        else:
            messages.error(request, 'Please correct the errors below.') 
    else:
        # For a GET request, display the form pre-filled with current profile data
        form = UserProfileEditForm(instance=user_profile)

    context = {
        'form': form,
        'profile': user_profile # Pass the profile for context, e.g., to display username or existing pic
    }
    return render(request, 'profiles/profile_edit.html', context)

#Login Redirect view
@login_required
def login_redirect_view(request):
    """
    Redirects users to the appropriate dashboard based on their group.
    """
    user = request.user
    if user.groups.filter(name='Employers').exists():
        # User is an Employer, redirect to employer dashboard
        return redirect('employers:employer_dashboard')
    elif user.groups.filter(name='JobSeekers').exists():
        return redirect('jobs:job_list') 
    else:
        print(f"Warning: User {user.username} logged in but is not in 'Employers' or 'JobSeekers' group.")
        return redirect('jobs:job_list') 
    
#Job application view
@login_required #
@require_POST #
def apply_for_job(request, job_pk):
    job_posting = get_object_or_404(JobPosting, pk=job_pk, is_active=True) #

    try:
        user_profile = request.user.profile #
        if not request.user.groups.filter(name='JobSeekers').exists(): #
            messages.error(request, "Only registered job seekers can apply for jobs.") #
            return redirect('jobs:job_detail', pk=job_pk) #
    except UserProfile.DoesNotExist: #
        messages.error(request, "You need a complete profile to apply for jobs.") #
        return redirect('profiles:profile_edit') #

    existing_application = JobApplication.objects.filter(user_profile=user_profile, job_posting=job_posting).first() #
    application_action_message = "" # To store the main action message #

    # Prepare email details for JOB SEEKER (common for new and re-application)
    seeker_email_subject = f"Application Received for {job_posting.title}" #
    seeker_user_name = request.user.first_name if request.user.first_name else request.user.username #
    company_name = job_posting.company.name if job_posting.company else "the Company" #
    
    seeker_email_body = f"""Dear {seeker_user_name},

Thank you for applying for the position of "{job_posting.title}" at {company_name} through Joblify.

Your application has been successfully submitted. We have notified the employer, and they will review your profile. You will receive further notifications regarding the status of your application.

You can view your submitted applications on your Joblify dashboard.

Best regards,
The Joblify Team""" #

    if existing_application:
        if existing_application.status in ['withdrawn_by_applicant', 'rejected_by_employer']: #
            existing_application.status = 'submitted' #
            existing_application.application_date = timezone.now() #
            existing_application.save() #
            application_action_message = f"You have successfully re-applied for '{job_posting.title}'!" #
            
            # Attempt to send email to JOB SEEKER for re-application
            try:
                send_mail(
                    seeker_email_subject,
                    seeker_email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False 
                )
                messages.success(request, application_action_message + " A confirmation email has been sent.") #
            except Exception as e:
                print(f"Error sending re-application email to job seeker: {e}") 
                messages.success(request, application_action_message) 
                messages.warning(request, "There was an issue sending the confirmation email to you.") #
        else:
            messages.warning(request, f"Your application for '{job_posting.title}' is currently '{existing_application.get_status_display()}'. You cannot re-apply at this time.") #
    else:
        # No existing application, create a new one
        new_application = None # Initialize to handle potential creation failure
        try:
            new_application = JobApplication.objects.create( #
                user_profile=user_profile,
                job_posting=job_posting,
                status='submitted'
            )
            application_action_message = f"Successfully applied for '{job_posting.title}'!" #

            # Attempt to send email to JOB SEEKER for new application
            try:
                send_mail(
                    seeker_email_subject,
                    seeker_email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False 
                )
                messages.success(request, application_action_message + " A confirmation email has been sent to you.") #
            except Exception as e:
                print(f"Error sending new application email to job seeker: {e}") 
                messages.success(request, application_action_message) 
                messages.warning(request, "There was an issue sending the confirmation email to you.") #

            # ---- START: Notify Employers of New Application ----
            if new_application and job_posting.company:
                employers_to_notify = EmployerProfile.objects.filter(company=job_posting.company)
                applicant_full_name = user_profile.user.get_full_name() if user_profile.user.get_full_name() else user_profile.user.username
                application_date_formatted = new_application.application_date.strftime("%B %d, %Y at %I:%M %p")

                employer_email_subject = f"New Application Received: {job_posting.title}"
                employer_email_body_template = f"""Dear Hiring Team at {job_posting.company.name},

A new application has been submitted for your job posting: "{job_posting.title}".

Applicant: {applicant_full_name} ({user_profile.user.username})
Applied on: {application_date_formatted}

Please log in to your Joblify dashboard to review this application.

Regards,
The Joblify System"""

                employer_emails = [emp.user.email for emp in employers_to_notify if emp.user and emp.user.email]
                
                if employer_emails:
                    try:
                        send_mail(
                            employer_email_subject,
                            employer_email_body_template,
                            settings.DEFAULT_FROM_EMAIL,
                            employer_emails, # Send to all relevant employer emails
                            fail_silently=False
                        )
                        # Optionally, add a message for the applicant if needed, or log this success
                        print(f"Successfully sent new application notification to employers for job: {job_posting.title}")
                    except Exception as e:
                        print(f"Error sending new application notification to employers: {e}")
                        # Potentially log this error more formally
                else:
                    print(f"No employer emails found to notify for company: {job_posting.company.name}")
            # ---- END: Notify Employers of New Application ----

        except IntegrityError: #
            messages.error(request, "There was an issue submitting your application. It's possible you've already applied.") #
        except Exception as e: # Catch other potential errors during application creation #
            messages.error(request, f"An unexpected error occurred during application: {e}") #
            print(f"Error during new application creation: {e}") #

    return redirect('jobs:job_detail', pk=job_pk) #

#My Applications View
@login_required
def my_applications(request):
    """
    Displays a paginated list of all job applications submitted by the logged-in job seeker.
    """
    # Ensure the user is a job seeker and has a UserProfile
    try:
        user_profile = request.user.profile # Assuming related_name is 'profile'
    except UserProfile.DoesNotExist:
        messages.error(request, "You need a profile to view your applications.")
        # Redirect to profile creation/edit or a relevant page
        return redirect('profiles:profile_edit') # Or 'profiles:profile_view'
    
    if not request.user.groups.filter(name='JobSeekers').exists():
        messages.error(request, "This page is for job seekers only.")
        return redirect('jobs:job_list') # Or a generic home page

    # Fetch all job applications for this user's profile, ordered by most recent
    application_list = JobApplication.objects.filter(user_profile=user_profile).order_by('-application_date')

    # Pagination
    paginator = Paginator(application_list, 10) # Show 10 applications per page
    page_number = request.GET.get('page')
    try:
        paginated_applications = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_applications = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_applications = paginator.page(paginator.num_pages)

    context = {
        'applications': paginated_applications,
        'is_paginated': paginated_applications.has_other_pages(),
    }
    return render(request, 'profiles/my_applications.html', context)

#Applicant Profile Detail view
@login_required # For now, any logged-in user can see this. We can add employer-specific checks later.
def applicant_profile_detail(request, username):
    """
    Displays the profile of a specific job seeker (applicant).
    'username' is the username of the job seeker whose profile is to be viewed.
    """
    # Get the User object for the given username
    target_user = get_object_or_404(User, username=username)
    
    # Get the UserProfile associated with this user
    try:
        applicant_profile = target_user.profile 
    except UserProfile.DoesNotExist:
        raise Http404("Job seeker profile not found for this user.")
    except AttributeError:
        raise Http404("Profile attribute not found for this user.")

    context = {
        'profile': applicant_profile, # Pass the applicant's UserProfile to the template
        'viewed_user': target_user, # Pass the applicant's User object
    }
    return render(request, 'profiles/applicant_profile_display.html', context)

#withdraw application view
@login_required
@require_POST # This action should only be done via a POST request
def withdraw_application(request, application_pk):
    """
    Allows a job seeker to withdraw their own job application.
    """
    application = get_object_or_404(JobApplication, pk=application_pk)

    # Authorization check: Ensure the logged-in user owns this application by checking if the application's user_profile matches the request.user's profile.
    try:
        user_profile = request.user.profile # Assuming related_name is 'profile'
        if application.user_profile != user_profile:
            messages.error(request, "You are not authorized to withdraw this application.")
            return redirect('profiles:my_applications') # Or a generic error page
    except UserProfile.DoesNotExist:
        messages.error(request, "You need a profile to manage applications.")
        return redirect('jobs:job_list') # Or a generic error page

    # Check if the application can be withdrawn (e.g., not already hired or in a final state)
    if application.status in ['hired', 'rejected_by_employer', 'withdrawn_by_applicant']:
        messages.warning(request, f"This application for '{application.job_posting.title}' cannot be withdrawn as it is already in a final state ('{application.get_status_display()}').")
        return redirect('profiles:my_applications')

    # Update the status to 'withdrawn_by_applicant'
    application.status = 'withdrawn_by_applicant'
    application.save()

    messages.success(request, f"You have successfully withdrawn your application for '{application.job_posting.title}'.")
    return redirect('profiles:my_applications')