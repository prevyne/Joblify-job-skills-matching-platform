# Joblify: AI-Powered Job & Skill Matching Platform

**Joblify** is an intelligent job-skills matching platform designed to bridge the gap between tech talent and opportunities in Kenya. It leverages a custom-built AI engine to analyze, score, and rank candidates against job postings, providing a highly relevant and efficient experience for both employers and job seekers.

---

## Key Features

The platform is built with distinct, role-based functionality for job seekers and employers, all powered by a central AI matching engine.

### 🧠 AI Matching Engine (v2.0)

The core of Joblify is its sophisticated matching algorithm, which goes beyond simple keyword searching.

- **Hybrid Scoring Model:** Combines text analysis with structured data for more accurate results. The final match score is a weighted average of text similarity (70%) and experience level compatibility (30%).
- **Weighted Text Analysis:** The engine uses TF-IDF and Cosine Similarity, but with added intelligence:
    - **Skill Weighting:** Explicitly listed skills are given 3x more weight than words in the general description, ensuring core competencies are prioritized.
    - **N-Gram Analysis:** The model analyzes both single words and two-word phrases (e.g., "Java programming") to better understand context.
- **Experience Level Matching:** The engine compares the required experience level for a job with the applicant's declared level and contributes this to the final score.
- **Bi-Directional Matching:** The AI works for both parties:
    - **For Employers:** Sorts applicants by the highest match score for a specific job.
    - **For Job Seekers:** Sorts the job list to show the most relevant opportunities first based on their profile.

### 👤 Job Seeker Experience

- **Personalized Job Feed:** The main job list is automatically sorted to show jobs that best match the user's profile and skills.
- **Profile Management:** Users can create and edit a detailed profile, including a bio, profile picture, contact information, **experience level**, and a comprehensive list of their skills.
- **Application Tracking:** A personal dashboard to view all submitted applications and their current status (e.g., `Submitted`, `Viewed`, `Shortlisted`).
- **Seamless Application Process:** Apply for jobs, withdraw applications, and re-apply to previously withdrawn or rejected positions.

### 🏢 Employer Experience

- **AI-Ranked Applicant Pipeline:** The applicant viewer automatically sorts candidates by their match score, allowing employers to instantly see the most qualified individuals.
- **Company & Job Management:**
    - Create and manage a detailed company profile with a logo, description, and website.
    - Post new jobs with specific skill and experience level requirements.
    - Edit, activate, or deactivate job postings from a central dashboard.
- **Efficient Applicant Review:**
    - Filter applicants by their current status.
    - View any applicant's full profile.
    - Update an applicant's status with a single click.

### 📧 Automated Notification System

- An email-based notification system keeps all users informed of key events:
    - **Application Submitted:** Confirmation sent to the job seeker.
    - **New Applicant:** Notification sent to the employer.
    - **Status Change:** Notification sent to the job seeker whenever an employer updates their application status.

---

## Technology Stack

- **Backend:** Python, Django
- **AI/ML:** Scikit-learn
- **Database:** SQLite (for development)
- **Frontend:** Bootstrap 5, HTML, CSS
- **Version Control:** Git

---

## Local Development Setup

Follow these instructions to get the project running on your local machine.

### Prerequisites
- Python 3.10 or higher
- Git

### Installation Steps

**1. Create `requirements.txt` (If you haven't already):**
Before anyone can install the project's dependencies, you need to generate the `requirements.txt` file from your activated virtual environment.
```bash
pip freeze > requirements.txt
Commit this file to your repository.

2. Clone the Repository:

Bash

git clone <your-repository-url>
cd <repository-folder>
3. Set Up the Virtual Environment:

Bash

# Create the virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
4. Install Dependencies:

Bash

pip install -r requirements.txt
5. Set Up the Database:

Bash

# Create the database tables
python3 manage.py migrate
6. Create a Superuser:
This account is necessary to access the Django admin panel.

Bash

python3 manage.py createsuperuser
Follow the prompts to create your admin username and password.

7. Create User Groups (Crucial Step):
The application relies on two user groups: JobSeekers and Employers.

Run the server: python3 manage.py runserver

Go to the admin panel: http://127.0.0.1:8000/admin/

Log in with your superuser account.

Go to the "Groups" section and click "Add Group".

Create a group named JobSeekers (the name must be exact, with the 'S').

Create another group named Employers (the name must be exact, with the 's').

8. Run the Project:

Bash

python3 manage.py runserver
The application will now be running at http://127.0.0.1:8000/. You can now create job seeker and employer accounts through the website's signup forms.

This README was last updated on July 16, 2025.