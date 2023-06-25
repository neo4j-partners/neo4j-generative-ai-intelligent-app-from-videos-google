import time

import numpy as np 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from neo4j_driver import run_query
import streamlit.components.v1 as components

st.set_page_config(
    page_title="AFL Access All Areas Episodes",
    page_icon="🧠",
    layout="wide",
)

st.title("AFL Access All Areas")

@st.cache_data
def get_data() -> pd.DataFrame:
    return run_query("""
      MATCH (n:Episode) return n.episode as Episode, 
      n.title as Title, n.synopsis as Synopsis,
      n.img as Image, n.id as Id, n.videoUrl as Url ORDER BY Id""")

@st.cache_data
def get_headlines() -> pd.DataFrame:
    return run_query("""
      MATCH (n:Episode)-[:HAS_HEADLINE]->(h:Headline)
      return n.id as episode, h.name as headline
      """)

@st.cache_data
def get_themes() -> pd.DataFrame:
    return run_query("""
      MATCH (n:Episode)-[:HAS_THEME]->(h:Theme)
      return n.id as episode, h.name as theme
      """)

df_episodes = get_data()
df_headlines = get_headlines()
df_themes = get_themes()

placeholder = st.empty()

with placeholder.container():
    st.markdown("### Episodes")
    for index, row in df_episodes.iterrows():
        col1, mid, col2 = st.columns([0.3, 0.1, 0.6])
        with col1:
            st.markdown(f"""**Episode {row['Episode']}**""")
            st.image(row['Image'])
            st.markdown(f"""[Video]({row['Url']})""")
        with col2:
            st.markdown("""**Headlines**""")
            selected_rows = df_headlines[df_headlines['episode'] == row['Id']]
            result_string = '\n'.join(selected_rows['headline'].astype(str))
            st.markdown(result_string)

            st.markdown("""**Themes**""")
            selected_rows = df_themes[df_themes['episode'] == row['Id']]
            result_string = ', '.join(selected_rows['theme'].astype(str))
            st.markdown(result_string)

            st.markdown("""**Synopsis**""")
            st.markdown(row['Synopsis'])

        st.markdown("---")

    st.markdown("### Episodes Metadata")
    st.dataframe(df_episodes)