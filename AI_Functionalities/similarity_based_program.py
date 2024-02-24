import csv
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('stopwords')

def preprocess_text(text):
    # Tokenize, remove stopwords, and apply stemming
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    tokens = nltk.word_tokenize(text.lower())
    stemmed_tokens = [stemmer.stem(token) for token in tokens if token.isalnum() and token not in stop_words]
    return ' '.join(stemmed_tokens)

def load_knowledge_base(file_path):
    # Load knowledge base from CSV file
    kb = {}
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 2:
                question = preprocess_text(row[0])
                answer = row[1]
                kb[question] = answer
    return kb

def get_answer(user_query, knowledge_base):
    #threshold score
    threshold = 0.5
    
    # Preprocess user query
    preprocessed_query = preprocess_text(user_query)

    # Prepare TF-IDF vectors
    corpus = list(knowledge_base.keys()) + [preprocessed_query]
    tfidf_vectorizer = TfidfVectorizer(use_idf=True, sublinear_tf=True)
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)

    # Calculate cosine similarity
    similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

    # Find the index of the most similar question
    most_similar_index = similarity_scores.argmax()

    # Return the corresponding answer
    #return knowledge_base.get(corpus[most_similar_index], "I'm sorry, I don't understand.")

    # Check if the similarity score meets the threshold
    if similarity_scores[most_similar_index] >= threshold:
        # Return the corresponding answer
        return knowledge_base.get(corpus[most_similar_index], "I'm sorry, I don't understand.")
    else:
        return "I'm sorry, I don't have enough information to answer that."