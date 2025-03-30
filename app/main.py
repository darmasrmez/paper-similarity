import streamlit as st

st.title('Paper similarity')

with st.form(key='paper'):
    st.write('Enter a query to search similarityt papers in arXiv or PubMed')
    st.text_input('Enter a Title')
    st.text_input('Enter an Abstract')
    st.form_submit_button('Submit')

st.button('Get papers from arXiv')
st.button('Get papers from PubMed')