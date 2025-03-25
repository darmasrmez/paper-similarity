import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import wordnet as wn

nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger_eng')
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
        if (token.replace('-', '').isalpha() and tag not in POS_TO_REMOVE
            and token not in stopwords.words('english')):
            if '-' in token:
                parts = token.split('-')
                lemmatized_parts = [
                    lemmatizer.lemmatize(part, get_wordnet_pos(tag))
                    for part in parts
                ]
                filtered_token = ' '.join(lemmatized_parts)
            else:
                filtered_token = lemmatizer.lemmatize(token, get_wordnet_pos(tag))
            filtered_tokens.append(filtered_token)

    return ' '.join(filtered_tokens)

df_arxiv = pd.read_csv('../data/arxiv_raw_corpus.csv')
df_arxiv['Title'] = df_arxiv['Title'].apply(normalize_text)
df_arxiv['Abstract'] = df_arxiv['Abstract'].apply(normalize_text)
df_arxiv.to_csv('./arxiv_normalized_corpus.csv', index=False)

df_pubmed = pd.read_csv('../data/pubmed_clean_corpus.csv')
df_pubmed['Title'] = df_pubmed['Title'].apply(normalize_text)
df_pubmed['Abstract'] = df_pubmed['Abstract'].apply(normalize_text)
df_pubmed.to_csv('./pubmed_normalized_corpus.csv', index=False)

print("¡Normalización completada y archivos guardados!")