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
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = [
            'bio', 
            'profile_picture', 
            'phone_number',
            'location',
            'experience_level', 
            'skills'
        ]
        # --- THIS WIDGETS SECTION IS UPDATED ---
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            # This tells Django to render the experience_level field
            # with the 'form-select' class for proper Bootstrap styling.
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.profile_picture:
            self.fields['profile_picture'].required = False