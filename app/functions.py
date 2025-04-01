import numpy as np
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

def load_vectorized_corpus(corpus_path):
    with open(corpus_path, 'rb') as f:
        document_vectors = pickle.load(f)
    vectorizer_path = corpus_path.replace('.pkl', '_vectorizador.pkl')
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    return document_vectors, vectorizer

def compute_cosine_similarity(query_text, corpus_vectors, vectorizer, document_names):
    query_text = normalize_text(query_text)
    query_vector = vectorizer.transform([query_text])
    similarities = cosine_similarity(query_vector, corpus_vectors)[0]
    sorted_indices = np.argsort(similarities)[::-1]
    top_10_indices = sorted_indices[:10]
    return pd.DataFrame({
        'Document': [document_names[i] for i in top_10_indices],
        'Similarity': [similarities[i] for i in top_10_indices]
    })

def process_query(file_path, content_type, method, ngram):
    df = pd.read_csv(file_path)
    if content_type not in df.columns:
        raise ValueError("Columna no encontrada en el archivo.")
    df[content_type] = df[content_type].apply(normalize_text)
    corpus = df[content_type].tolist()
    document_vectors, vectorizer = vectorize_corpus(corpus, method, ngram)
    return document_vectors, vectorizer, df['Title'].tolist()
