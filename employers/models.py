from django.db import models
from django.contrib.auth.models import User
from jobs.models import Company # Assuming your Company model is in the 'jobs' app

class EmployerProfile(models.Model):
    """
    Represents the profile for an employer user, linking them to a company.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='employer_profile',
        help_text="The user account associated with this employer profile."
    )
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, # Or models.SET_NULL if an employer can exist without a company temporarily
        related_name='employer_profiles',
        help_text="The company this employer represents."
    )
    position_in_company = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Employer's role or position within the company (e.g., HR Manager, Recruiter)."
    )
    phone_number = models.CharField(
        max_length=25, # Increased length for international numbers or extensions
        blank=True, 
        null=True,
        help_text="Contact phone number for the employer (optional)."
    )
    # I might add other fields here later, e.g.:
    # is_company_admin = models.BooleanField(default=False, help_text="Can this employer manage the company profile?")
    # date_joined_company = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Employer Profile"
        verbose_name_plural = "Employer Profiles"
        ordering = ['company', 'user__username']

    def __str__(self):
        return f"{self.user.username} at {self.company.name}"

    # Optional: A property to easily access company details if needed
    @property
    def company_name(self):
        return self.company.name
