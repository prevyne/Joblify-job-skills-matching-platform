from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Skill

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=150, required=False, help_text='Optional.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)
        
class UserProfileEditForm(forms.ModelForm):
    # Use a ModelMultipleChoiceField with a widget for better UX with skills
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all().order_by('name'), # Show all available skills, ordered
        widget=forms.CheckboxSelectMultiple, # Render as checkboxes, or use SelectMultiple
        required=False # Make it optional to have skills
    )

    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'phone_number', 'location', 'skills']
        # Exclude 'user' field as it should not be changed via this form; it's set by who is logged in.
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}), # Make bio a bit larger
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.profile_picture:
            self.fields['profile_picture'].required = False # Don't require a new picture if one exists
