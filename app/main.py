import streamlit as st

st.title('Paper similarity')

st.markdown(
    """**Team**:
    \n* Armas Ramírez Daniel
    \n* Prezas Bernal Emiliano
    \n* Escamilla Gachuz Karla Esther
    \n* Dorado Alcalá Nataly
    """
)

st.subheader("Form")
with st.form(key='paper'):
    col1, col2 = st.columns(2)
    with col1:
        ris_file = st.file_uploader("Choose RIS file", type = 'ris')
    with col2:
        bib_file = st.file_uploader("Choose RIS file", type ='bib')

    content = st.radio(
        "What do you want to extract?",
        ['Title', 'Abstract'],
        index=None
    )
    vector_model = st.radio(
        "which representation do you wish to use?",
        ['count-unigram', 'count-binary-unigram', 'count-bigram', 'count-binary-bigram',
         'tf-idf-unigram', 'tf-idf-binary-unigram', 'tf-idf-bigram', 'tf-idf-binary-bigram'],
        index=None
    )
    st.form_submit_button('Get similarity')

st.markdown("### Top 10")