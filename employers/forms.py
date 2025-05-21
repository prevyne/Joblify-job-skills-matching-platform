from django import forms
from django.contrib.auth.forms import UserCreationForm # Keep for EmployerSignUpForm
from django.contrib.auth.models import User # Keep for EmployerSignUpForm
from jobs.models import Company, JobPosting # Import JobPosting and Skill from jobs app
from profiles.models import Skill

class EmployerSignUpForm(UserCreationForm):
    """
    Form for employers to sign up.
    Includes standard user creation fields plus company information.
    """
    email = forms.EmailField(
        max_length=254, 
        required=True, 
        help_text='Required. Please provide a valid company email address.'
    )
    company_name = forms.CharField(
        max_length=255, 
        required=True, 
        help_text='Required. The legal name of your company.'
    )
    company_website = forms.URLField(
        max_length=200, 
        required=False,
        help_text='Optional. Your company\'s official website (e.g., https://www.example.com).'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',) # Add email to the UserCreationForm fields

    def clean_company_name(self):
        """
        Custom validation for company name if needed.
        For now, just returns the cleaned data.
        You could add checks here, e.g., to prevent certain names.
        """
        company_name = self.cleaned_data.get('company_name')
        return company_name
    
class JobPostingForm(forms.ModelForm):
    """
    Form for employers to create and edit job postings.
    """
    skills_required = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select the skills required for this job."
    )

    # Example of adding a date picker widget for application_deadline
    application_deadline = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        help_text="Optional. When do applications close?"
    )

    class Meta:
        model = JobPosting
        fields = [
            'title', 'description', 'responsibilities', 'qualifications', 
            'location', 'job_type', 'experience_level', 
            'salary_min', 'salary_max', 'skills_required', 'application_deadline',
            'is_active'
        ]
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'responsibilities': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'qualifications': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # skills_required is handled by the explicit field definition above for widget choice
        }

        labels = {
            'is_active': "Make this job posting active immediately?",
            'salary_min': "Minimum Salary (KES, optional)",
            'salary_max': "Maximum Salary (KES, optional)",
        }
        
        help_texts = {
            'location': "e.g., Nairobi CBD, Remote, Nakuru County",
            'is_active': "If unchecked, the job will be saved as a draft.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure skills_required queryset is fresh if skills can be added dynamically
        self.fields['skills_required'].queryset = Skill.objects.all().order_by('name')

#Company edit form         
class CompanyEditForm(forms.ModelForm):
    """
    Form for employers to edit their company's profile.
    """
    class Meta:
        model = Company
        fields = ['name', 'description', 'website', 'logo', 'location']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.example.com'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}), # Allows clearing existing logo
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Nairobi CBD, Kenya'}),
        }
        labels = {
            'name': "Company Name",
            'description': "Company Overview/About Us",
            'website': "Company Website URL",
            'logo': "Company Logo",
            'location': "Main Office Location",
        }
        help_texts = {
            'logo': "Upload your company's logo. If you want to change it, upload a new one. To remove it, check 'Clear'.",
            'website': "Ensure it starts with http:// or https://",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make logo not required if one already exists
        if self.instance and self.instance.logo:
            self.fields['logo'].required = False

    def clean_name(self):
        name = self.cleaned_data.get('name')
        return name