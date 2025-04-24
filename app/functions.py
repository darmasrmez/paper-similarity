import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pickle
import re
import nltk
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import wordnet as wn
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
POS_TO_REMOVE = {'DT', 'IN', 'CC', 'PRP', 'PRP$'}

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wn.ADJ
    elif treebank_tag.startswith('V'):
        return wn.VERB
    elif treebank_tag.startswith('R'):
        return wn.ADV
    else:
        return wn.NOUN

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    tokens = word_tokenize(text)
    tagged_tokens = pos_tag(tokens)

    filtered_tokens = []
    for token, tag in tagged_tokens:
        if token in stop_words or tag in POS_TO_REMOVE:
            continue
        if token in re.escape(".,;:!?()[]{}\"'"):
            continue
        if '-' in token:
            parts = token.split('-')
            lemmatized_parts = [
                lemmatizer.lemmatize(part, get_wordnet_pos(tag)) for part in parts
            ]
            filtered_token = ' '.join(lemmatized_parts)
        else:
            filtered_token = lemmatizer.lemmatize(token, get_wordnet_pos(tag))
        filtered_tokens.append(filtered_token)

    return ' '.join(filtered_tokens)


def vectorize_corpus(corpus, method, ngram):
    token_pattern = r'(?u)\w+|[^\w\s]'
    if method == "count":
        vectorizer = CountVectorizer(token_pattern=token_pattern, ngram_range=ngram)
    elif method == "binary":
        vectorizer = CountVectorizer(binary=True, token_pattern=token_pattern, ngram_range=ngram)
    elif method == "tf-idf":
        vectorizer = TfidfVectorizer(token_pattern=token_pattern, ngram_range=ngram)
    else:
        raise ValueError("Método no válido")
    return vectorizer.fit_transform(corpus), vectorizer

def vectorize_corpus(corpus, method, ngram):
    token_pattern = r'(?u)\w+|[^\w\s]'
    if method == "count":
        vectorizer = CountVectorizer(token_pattern=token_pattern, ngram_range=ngram)
    elif method == "binary":
        vectorizer = CountVectorizer(binary=True, token_pattern=token_pattern, ngram_range=ngram)
    elif method == "tf-idf":
        vectorizer = TfidfVectorizer(token_pattern=token_pattern, ngram_range=ngram)
    else:
        raise ValueError("Método no válido")
    return vectorizer.fit_transform(corpus), vectorizer

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
        'index': [sorted_indices[i] for i in top_10_indices],
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
