import streamlit as st

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

st.image("https://raw.githubusercontent.com/neo4j-partners/intelligent-app-from-videos-google-generativeai-neo4j/main/notebook/images/arch.png?token=GHSAT0AAAAAAB6WIGG3H6N3BBHYWQX7AELUZEYB6PA")
st.markdown("""
---

This the schema in which the Vide transcripts are stored in Neo4j
""")
st.image("https://raw.githubusercontent.com/neo4j-partners/intelligent-app-from-videos-google-generativeai-neo4j/main/notebook/images/schema.png?token=GHSAT0AAAAAAB6WIGG3KUV5FFXQ3EZZG7NWZEYCBUA")
st.markdown("""
---

This is how the Chatbot flow goes:
""")
st.image("https://raw.githubusercontent.com/neo4j-partners/intelligent-app-from-videos-google-generativeai-neo4j/main/notebook/images/langchain-neo4j.png?token=GHSAT0AAAAAAB6WIGG3BDVPU3RSPAGQ3E3AZEYB7VA")
