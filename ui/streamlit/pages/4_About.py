import streamlit as st
from PIL import Image

st.set_page_config(page_icon="🧠", layout="wide")
st.markdown("""
This is a Proof of Concept application which shows how Google Vertex AI Generative AI can be used with Neo4j to build and consume Knowledge Graphs using Video Transcripts.
Transcript data are from [AFL after-match Commentary](https://www.afl.com.au/ondemand/shows/490977/access-all-areas?episode=1#2023).
Using Google Vertex AI Generative AI's `text-bison` and `code-bison` models, transcripts are converted to Knowledge Graph.

### Why Neo4j is a great addition to Google Generative AI:
- *Fine-grained access control of your data* : You can control who can and cannot access parts of your data
- Greater reliability with factual data
- More Explainability
- Domain specificity
- Ability to gain insights using Graph Algorithms
- Vector embedding support and Similarity Algorithms on Neo4j

""", unsafe_allow_html=True)

arch = Image.open('./images/arch.png')
langchain = Image.open('./images/langchain-neo4j.png')
schema = Image.open('./images/schema.png')

st.image(arch)
st.markdown("""
---

This the schema in which the Vide transcripts are stored in Neo4j
""")
st.image(schema)
st.markdown("""
---

This is how the Chatbot flow goes:
""")
st.image(langchain)
