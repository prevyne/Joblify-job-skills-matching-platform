from django.contrib import admin
from .models import Skill, UserProfile, JobApplication # ADD JobApplication to imports

# Register your models here so they appear in the admin interface

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'skill_type')
    search_fields = ('name',)
    list_filter = ('skill_type',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_username', 'phone_number', 'location')
    search_fields = ('user__username', 'user__email', 'location')
    raw_id_fields = ('user', 'skills') # Makes user and skills fields easier to manage if there are many

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'
    user_username.admin_order_field = 'user__username'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('user_profile_username', 'job_posting_title', 'application_date', 'status')
    list_filter = ('status', 'application_date', 'job_posting__company__name') # Added company name for filtering
    search_fields = ('user_profile__user__username', 'job_posting__title', 'job_posting__company__name', 'status')
    date_hierarchy = 'application_date'
    raw_id_fields = ('user_profile', 'job_posting') # Useful for ForeignKey fields with many options
    list_editable = ('status',) # Allows editing status directly in the list view
    list_per_page = 20 # Show 20 applications per page in admin

    fieldsets = (
        (None, {
            'fields': ('user_profile', 'job_posting')
        }),
        ('Application Details', {
            'fields': ('application_date', 'status') # Add other fields like cover_letter_text if implemented
        }),
    )
    readonly_fields = ('application_date',) # application_date is auto_now_add

    def user_profile_username(self, obj):
        return obj.user_profile.user.username
    user_profile_username.short_description = 'Applicant' # Changed from 'Applicant (Username)'
    user_profile_username.admin_order_field = 'user_profile__user__username'

    def job_posting_title(self, obj):
        return obj.job_posting.title
    job_posting_title.short_description = 'Job Title'
    job_posting_title.admin_order_field = 'job_posting__title'
