from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(text1, text2):
    """
    Calculates the cosine similarity between two text strings.
    Returns a float between 0.0 and 1.0.
    """
    # Ensure we don't process empty strings, which can cause errors.
    if not text1 or not text2:
        return 0.0

    documents = [text1, text2]
    
    try:
        # Using stop_words='english' helps ignore common words like 'the', 'a', 'is'.
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
        
        # Calculate and return the similarity score
        similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity_score
    except Exception:
        # If any error occurs during vectorization (e.g., text with only stop words), return 0.
        return 0.0