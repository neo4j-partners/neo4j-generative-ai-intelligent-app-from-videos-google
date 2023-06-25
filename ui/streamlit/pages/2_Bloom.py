import streamlit as st

st.set_page_config(
    page_title="AFL - Neo4j Bloom",
    page_icon="🧠",
    layout="wide",
)

st.title("Knowledge Graph Exploration")

placeholder = st.empty()

with placeholder.container():
    st.markdown("""
        <style>
            iframe {
                position: fixed;
                background: #000;
                border: none;
                top: 0; right: 0;
                bottom: 0; left: 0;
                width: 100%;
                height: 100%;
            }
        </style>
        <iframe 
            src="https://workspace-preview.neo4j.io/workspace/explore" 
            frameborder="0" style="overflow:hidden;height:100%;width:100%" 
            height="100%" width="100%" title="Bloom">
        </iframe>
    """, unsafe_allow_html=True)
