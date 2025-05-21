from django.contrib import admin
from .models import EmployerProfile

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'position_in_company', 'phone_number')
    search_fields = ('user__username', 'company__name', 'position_in_company')
    list_filter = ('company',)
    raw_id_fields = ('user', 'company') # Useful for ForeignKey/OneToOneField with many options