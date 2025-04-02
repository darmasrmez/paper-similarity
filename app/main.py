import streamlit as st
from functions import load_vectorized_corpus, compute_cosine_similarity
from bibtexparser import loads as bibtex_loads
from rispy import load as ris_load
import pickle
import io
import os
import pandas as pd


st.set_page_config(page_title="Top 10 Similar Papers", layout="centered")
st.title('🔍 Top 10 Similar Papers')

def parse_query_file(file, file_type):
    content = file.read().decode('utf-8')
    if file_type == 'bib':
        bib_db = bibtex_loads(content)
        if not bib_db.entries:
            return None
        entry = {k.lower(): v for k, v in bib_db.entries[0].items()}
        return {
            'title': entry.get('title', ''),
            'abstract': entry.get('abstract', ''),
        }
    else:
        return ris_load(io.StringIO(content))[0]

VECTOR_MAP = {
    'count-unigram': ('frecuencia', 'unigramas'),
    'count-bigram': ('frecuencia', 'bigramas'),
    'binary-unigram': ('binaria', 'unigramas'),
    'binary-bigram': ('binaria', 'bigramas'),
    'tf-idf-unigram': ('tfidf', 'unigramas'),
    'tf-idf-bigram': ('tfidf', 'bigramas')
}

# Formulario
with st.form(key='search_form'):
    file_type = st.radio("File type:", ['RIS', 'BibTeX'], horizontal=True)
    query_file = st.file_uploader("Upload File", type=['.bib', '.ris'])
    content_type = st.selectbox("Compare by:", ['Title', 'Abstract'])
    vector_model = st.selectbox("Vector model:",
                              ['count-unigram', 'count-bigram',
                               'binary-unigram', 'binary-bigram',
                               'tf-idf-unigram', 'tf-idf-bigram'])
    submitted = st.form_submit_button("Find Top 10")

# Procesamiento
if submitted and query_file:
    try:
        # Parsear consulta
        actual_file_type = 'bib' if file_type == 'BibTeX' else 'ris'
        query_data = parse_query_file(query_file, actual_file_type)
        if not query_data:
            st.error("Could not parse the uploaded file")
            st.stop()

        query_text = query_data.get('title' if content_type == 'Title' else 'abstract', '')
        if not query_text:
            st.error(f"No {content_type} found in the uploaded file")
            st.stop()

        vector_method, ngram_type = VECTOR_MAP[vector_model]
        all_results = []

        for corpus in ['arxiv', 'pubmed']:
            try:

                df_arxiv = pd.read_csv("/home/darmasrmz/IPN/7/NLP/research-similarity/data/arxiv_clean_corpus.csv")
                df_pubmed = pd.read_csv("/home/darmasrmz/IPN/7/NLP/research-similarity/data/pubmed_clean_corpus.csv")
                base_path = "/home/darmasrmz/IPN/7/NLP/research-similarity/app/"
                corpus_prefix = corpus.lower()
                matrix_path = base_path + f"{corpus_prefix}_{content_type}_{vector_method}_{ngram_type}.pkl"
                vectorizer_path = base_path + f"{corpus_prefix}_{content_type}_vectorizador_{vector_method}_{ngram_type}.pkl"

                vectors = []
                print(matrix_path)
                with open(matrix_path, 'rb') as f:
                    vectors = pickle.load(f)

                vectorizer = None
                with open(vectorizer_path, 'rb') as f:
                    vectorizer = pickle.load(f)

                document_names = vectorizer.get_feature_names_out() if hasattr(vectorizer, 'get_feature_names_out') else []

                print(document_names)
                results = compute_cosine_similarity(
                    query_text=query_text,
                    corpus_vectors=vectors,
                    vectorizer=vectorizer,
                    document_names=document_names
                )

                results['Corpus'] = corpus
                all_results.append(results)

            except FileNotFoundError as e:
                st.warning(f"Files not found for {corpus}: {str(e)}")
                continue
            except Exception as e:
                st.warning(f"Error processing {corpus}: {str(e)}")
                continue

        if not all_results:
            st.error("No results found. Please check your input files.")
            st.stop()

        top_results = pd.concat(all_results).sort_values('Similarity', ascending=False).head(10)
        top_results['Similarity'] = top_results['Similarity'].round(4)
        def get_title(row):
            corpus = row['Corpus']
            index_ = row['index']
            if corpus == 'arxiv':
                return df_arxiv.loc[index_, 'Title']
            else:
                return df_pubmed.loc[index_, 'Title']

        top_results['Paper'] = top_results.apply(get_title, axis=1)

        st.subheader("Top 10 Most Similar Papers:")
        st.dataframe(
            top_results[['Similarity', 'index', 'Corpus', 'Paper']],
            hide_index=True,
            column_config={
                "Similarity": st.column_config.NumberColumn(format="%.4f"),
                "Document": st.column_config.Column(width="large")
            }
        )

    except Exception as e:
        st.error(f"Processing error: {str(e)}")
elif submitted:
    st.warning("Please upload a file first")