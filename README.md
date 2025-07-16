# Joblify - AI-Powered Job Skill Matching Platform

An intelligent job-skills matching platform designed to connect tech talent with opportunities in Kenya. Joblify leverages Natural Language Processing to score and rank candidates based on their relevance to a job posting, helping employers find the best fit faster.

---

## Key Features Implemented

The platform is divided into three core modules: Job Seeker features, Employer features, and the AI Matching Engine.

###  Core Platform & Technology
- **Backend Framework:** Built with Django 5.2.
- **Database:** Uses SQLite for development.
- **Frontend:** Styled with Bootstrap 5 for a responsive UI.
- **AI Engine:** Powered by Python's `scikit-learn` library.
- **Development:** Follows best practices including virtual environments and Git feature branching.

### 👤 Job Seeker Functionality
- **Authentication:** Secure user signup, login, and logout.
- **Profile Management:** Users can create and edit a detailed profile, including a bio, profile picture, contact information, and a list of skills.
- **Job Discovery:** View a paginated list of all active job postings with a keyword search function.
- **Application Process:**
    - View detailed job descriptions.
    - Apply for jobs with a single click.
    - Withdraw applications.
    - Re-apply for jobs if a previous application was withdrawn or rejected.
- **My Applications Dashboard:** A dedicated page to track the status of all submitted applications (`Submitted`, `Viewed`, `Shortlisted`, etc.).

### 🏢 Employer Functionality
- **Authentication & Setup:** Separate signup flow for employers to create user accounts and register their company profile.
- **Employer Dashboard:** A central hub showing a company overview, a summary of job postings (active/inactive), and quick links to core actions.
- **Company Profile Management:** Ability to edit company details, including name, description, website, and logo.
- **Job Post Management:**
    - Create new job postings with detailed descriptions and required skills.
    - Edit existing job postings.
    - Activate or deactivate jobs directly from a management dashboard.
- **Applicant Tracking System (ATS):**
    - View a list of all applicants for a specific job posting.
    - **AI-Powered Ranking:** Applicants are automatically sorted by a **Match Score**, placing the most relevant candidates at the top.
    - Filter applicants by their application status (e.g., view all 'Shortlisted' candidates).
    - View the detailed profile of any applicant in a read-only format.
    - Update the status of an application (e.g., from 'Submitted' to 'Shortlisted').

### 🧠 AI Matching Engine (v1.0)
- **Core Technology:** Utilizes **TF-IDF (Term Frequency-Inverse Document Frequency)** to analyze text and **Cosine Similarity** to measure relevance.
- **Process:** The engine compares the text from a job posting (title, description, skills) against the text from an applicant's profile (bio, skills).
- **Output:** Generates a "Match Score" percentage for each applicant, which is displayed visually with a progress bar in the applicant list.

### 📧 Notification System
- **Email-based notifications** are sent for key events:
    1.  **To Job Seeker:** Confirmation when an application is successfully submitted.
    2.  **To Employer:** Notification when a new application is received for their job posting.
    3.  **To Job Seeker:** Notification when an employer updates the status of their application.

---

## Local Setup and Installation

To run this project locally, follow these steps:

**1. Create `requirements.txt`:**
Before you can install the dependencies, you need to generate the `requirements.txt` file from your current virtual environment. Run this command:
```bash
pip freeze > requirements.txt
