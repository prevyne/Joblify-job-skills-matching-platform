from django.db import models
from django.contrib.auth.models import User

#Company model
class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True) # Requires Pillow
    location = models.CharField(max_length=150, blank=True, null=True) # e.g., "Nairobi", "Nakuru"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies" # Corrects pluralization in admin
        ordering = ['name']
        
#Job Posting model
class JobPosting(models.Model):
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('junior', 'Junior Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead / Principal'),
    ]

    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_postings')
    description = models.TextField()
    responsibilities = models.TextField(blank=True, null=True) # Or break down further
    qualifications = models.TextField(blank=True, null=True) # Or break down further
    location = models.CharField(max_length=150, help_text="e.g., Nairobi, Remote, Nakuru")
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full-time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, blank=True, null=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # Optional
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # Optional
    skills_required = models.ManyToManyField('profiles.Skill', blank=True, related_name='job_postings_requiring_skill')
    is_active = models.BooleanField(default=True, help_text="Is this job posting currently active and visible?")
    date_posted = models.DateTimeField(auto_now_add=True)
    application_deadline = models.DateField(blank=True, null=True)
    # posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_postings_created') # If you track which user posted it

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    class Meta:
        ordering = ['-date_posted'] # Show newest jobs first by default