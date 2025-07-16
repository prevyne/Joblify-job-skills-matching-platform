from django.db import models
from django.contrib.auth.models import User # Import the User model
from jobs.models import JobPosting # Import JobPosting from the 'jobs' app

#Skills model
class Skill(models.Model):
    SKILL_TYPE_CHOICES = [
        ('technical', 'Technical'),
        ('soft', 'Soft'),
    ]
    name = models.CharField(max_length=100, unique=True) # e.g., "Python", "Communication"
    skill_type = models.CharField(
        max_length=10,
        choices=SKILL_TYPE_CHOICES,
        default='technical',
    )
    #A brief description of the skill
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_skill_type_display()})"

    class Meta:
        ordering = ['name'] # Orders skills alphabetically by name by default
        
#User Profile model
class UserProfile(models.Model):
    
    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry-Level'),
        ('mid', 'Mid-Level'),
        ('senior', 'Senior'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile') # Link to Django's User model
    bio = models.TextField(blank=True, null=True) # A short biography or summary
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True) # For user's photo
    skills = models.ManyToManyField(Skill, blank=True) # Many users can have many skills
    phone_number = models.CharField(max_length=20, blank=True, null=True) # Optional phone number
    location = models.CharField(max_length=100, blank=True, null=True) # e.g., "Nairobi", "Nakuru"

    experience_level = models.CharField(
        max_length=10,
        choices=EXPERIENCE_LEVEL_CHOICES,
        null=True,  # Important: Allows existing profiles to have no value
        blank=True  # Important: Makes the field optional in forms
    )


    def __str__(self):
        return f"{self.user.username}'s Profile"

    # Property to easily access the user's full name if set
    @property
    def full_name(self):
        return self.user.get_full_name() if self.user.get_full_name() else self.user.username
    
#Job Application Model
class JobApplication(models.Model):
    """
    Represents a job application submitted by a UserProfile for a JobPosting.
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('viewed', 'Viewed by Employer'),
        ('shortlisted', 'Shortlisted'),
        ('interviewing', 'Interviewing'),
        ('offered', 'Offered'),
        ('rejected_by_employer', 'Rejected by Employer'), # More specific
        ('withdrawn_by_applicant', 'Withdrawn by Applicant'), # If applicant can withdraw
        ('hired', 'Hired'),
    ]

    user_profile = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='applications',
        help_text="The profile of the user who applied."
    )
    job_posting = models.ForeignKey(
        JobPosting, 
        on_delete=models.CASCADE, 
        related_name='applicants',
        help_text="The job posting for which the user applied."
    )
    application_date = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time the application was submitted."
    )
    status = models.CharField(
        max_length=30, # Increased length to accommodate longer status keys
        choices=STATUS_CHOICES,
        default='submitted',
        help_text="The current status of the application."
    )
    # Optional fields for later enhancement:
    # cover_letter_text = models.TextField(
    #     blank=True, 
    #     null=True,
    #     help_text="A brief cover letter or note from the applicant."
    # )
    # resume_snapshot = models.FileField( # Could store a specific resume version used for this application
    #     upload_to='application_resumes/', 
    #     blank=True, 
    #     null=True,
    #     help_text="A snapshot of the resume used for this specific application (optional)."
    # )

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        # Ensure a user can only apply once for the same job
        unique_together = ('user_profile', 'job_posting')
        ordering = ['-application_date'] # Show newest applications first

    def __str__(self):
        return f"{self.user_profile.user.username}'s application for {self.job_posting.title} ({self.get_status_display()})"