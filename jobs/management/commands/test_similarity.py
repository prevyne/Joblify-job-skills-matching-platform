from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Command(BaseCommand):
    help = 'Tests the text similarity calculation using TF-IDF and Cosine Similarity'

    def handle(self, *args, **options):
        self.stdout.write("Running AI Similarity Test...")

        # --- Sample Data ---
        # A sample job description
        job_description = """
        We are seeking a Python Developer with experience in Django and REST APIs.
        The ideal candidate will have strong skills in database management with PostgreSQL
        and front-end development using JavaScript. Experience with Docker is a plus.
        """

        # A sample applicant profile/CV text
        applicant_cv = """
        Experienced Python and Django developer with a background in building web applications.
        Proficient with PostgreSQL databases and creating RESTful APIs.
        Familiar with basic front-end JavaScript frameworks.
        """

        # --- AI Calculation ---
        # 1. Place the two documents into a list
        documents = [job_description, applicant_cv]

        # 2. Create the TF-IDF Vectorizer
        # This object will convert text into a matrix of TF-IDF features.
        tfidf_vectorizer = TfidfVectorizer()

        # 3. Fit and transform the documents
        # This learns the vocabulary and calculates the TF-IDF vectors.
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

        # 4. Calculate Cosine Similarity
        # This compares the first document (job) to the second (applicant).
        # The result is a matrix, so we get the specific value at [0, 1].
        similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        # 5. Output the result
        self.stdout.write(self.style.SUCCESS(f"\nJob Description:\n{job_description}"))
        self.stdout.write(self.style.SUCCESS(f"\nApplicant CV:\n{applicant_cv}"))
        self.stdout.write(self.style.WARNING(f"\nCalculated Similarity Score: {similarity_score:.4f}"))

        # Convert to a percentage for a more user-friendly feel
        match_percentage = similarity_score * 100
        self.stdout.write(self.style.SUCCESS(f"Match Percentage: {match_percentage:.2f}%"))