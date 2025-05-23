# Generated by Django 5.2.1 on 2025-05-20 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_jobapplication'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobapplication',
            name='status',
            field=models.CharField(choices=[('submitted', 'Submitted'), ('viewed', 'Viewed by Employer'), ('shortlisted', 'Shortlisted'), ('interviewing', 'Interviewing'), ('offered', 'Offered'), ('rejected_by_employer', 'Rejected by Employer'), ('withdrawn_by_applicant', 'Withdrawn by Applicant'), ('hired', 'Hired')], default='submitted', help_text='The current status of the application.', max_length=30),
        ),
    ]
