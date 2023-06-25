import time

import numpy as np 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from neo4j_driver import run_query
import streamlit.components.v1 as components

st.set_page_config(
    page_title="AFL Access All Areas",
    page_icon="🧠",
    layout="wide",
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
    </style>
    <div style='text-align: center; font-size: 2.5rem; font-weight: 600; font-family: "Roboto"; color: #018BFF; line-height:1; '>AFL Access All Areas</div>
    <div style='text-align: center; font-size: 1.5rem; font-weight: 300; font-family: "Roboto"; color: rgb(179 185 182); line-height:0; '>
        Powered by <svg width="80" height="60" xmlns="http://www.w3.org/2000/svg" id="Layer_1" data-name="Layer 1" viewBox="0 0 200 75"><path d="M39.23,19c-10.58,0-17.68,6.16-17.68,18.11v8.52A8,8,0,0,1,25,44.81a7.89,7.89,0,0,1,3.46.8V37.07c0-7.75,4.28-11.73,10.8-11.73S50,29.32,50,37.07V55.69h6.89V37.07C56.91,25.05,49.81,19,39.23,19Z"/><path d="M60.66,37.8c0-10.87,8-18.84,19.27-18.84s19.13,8,19.13,18.84v2.53H67.9c1,6.38,5.8,9.93,12,9.93,4.64,0,7.9-1.45,10-4.56h7.6c-2.75,6.66-9.27,10.94-17.6,10.94C68.63,56.64,60.66,48.67,60.66,37.8Zm31.15-3.62c-1.38-5.73-6.08-8.84-11.88-8.84S69.5,28.53,68.12,34.18Z"/><path d="M102.74,37.8c0-10.86,8-18.83,19.27-18.83s19.27,8,19.27,18.83-8,18.84-19.27,18.84S102.74,48.67,102.74,37.8Zm31.59,0c0-7.24-4.93-12.46-12.32-12.46S109.7,30.56,109.7,37.8,114.62,50.26,122,50.26,134.33,45.05,134.33,37.8Z"/><path d="M180.64,62.82h.8c4.42,0,6.08-2,6.08-7V20.16h6.89v35.2c0,8.84-3.48,13.4-12.32,13.4h-1.45Z"/><path d="M177.2,59.14h-6.89V50.65H152.86A8.64,8.64,0,0,1,145,46.2a7.72,7.72,0,0,1,.94-8.16L161.6,17.49a8.65,8.65,0,0,1,15.6,5.13V44.54h5.17v6.11H177.2ZM151.67,41.8a1.76,1.76,0,0,0-.32,1,1.72,1.72,0,0,0,1.73,1.73h17.23V22.45a1.7,1.7,0,0,0-1.19-1.68,2.36,2.36,0,0,0-.63-.09,1.63,1.63,0,0,0-1.36.73L151.67,41.8Z"/><path d="M191,5.53a5.9,5.9,0,1,0,5.89,5.9A5.9,5.9,0,0,0,191,5.53Z" fill="#018bff"/><path d="M24.7,47a5.84,5.84,0,0,0-3.54,1.2l-6.48-4.43a6,6,0,0,0,.22-1.59A5.89,5.89,0,1,0,9,48a5.81,5.81,0,0,0,3.54-1.2L19,51.26a5.89,5.89,0,0,0,0,3.19l-6.48,4.43A5.81,5.81,0,0,0,9,57.68a5.9,5.9,0,1,0,5.89,5.89A6,6,0,0,0,14.68,62l6.48-4.43a5.84,5.84,0,0,0,3.54,1.2A5.9,5.9,0,0,0,24.7,47Z" fill="#018bff"/></svg> | 
        <svg height="60" width="120" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><path d="M32.377 26.446h-12.52v3.715h8.88c-.44 5.2-4.773 7.432-8.865 7.432a9.76 9.76 0 0 1-9.802-9.891c0-5.624 4.354-9.954 9.814-9.954 4.212 0 6.694 2.685 6.694 2.685l2.6-2.694s-3.34-3.717-9.43-3.717c-7.755 0-13.754 6.545-13.754 13.614 0 6.927 5.643 13.682 13.95 13.682 7.307 0 12.656-5.006 12.656-12.408 0-1.562-.227-2.464-.227-2.464z" fill="#4885ed"/><use xlink:href="#A" fill="#db3236"/><use xlink:href="#A" x="19.181" fill="#f4c20d"/><path d="M80.628 23.765c-4.716 0-8.422 4.13-8.422 8.766 0 5.28 4.297 8.782 8.34 8.782 2.5 0 3.83-.993 4.8-2.132v1.73c0 3.027-1.838 4.84-4.612 4.84-2.68 0-4.024-1.993-4.5-3.123l-3.372 1.4c1.196 2.53 3.604 5.167 7.9 5.167 4.7 0 8.262-2.953 8.262-9.147V24.292H85.36v1.486c-1.13-1.22-2.678-2.013-4.73-2.013zm.34 3.44c2.312 0 4.686 1.974 4.686 5.345 0 3.427-2.37 5.315-4.737 5.315-2.514 0-4.853-2.04-4.853-5.283 0-3.368 2.43-5.378 4.904-5.378z" fill="#4885ed"/><path d="M105.4 23.744c-4.448 0-8.183 3.54-8.183 8.76 0 5.526 4.163 8.803 8.6 8.803 3.712 0 6-2.03 7.35-3.85l-3.033-2.018c-.787 1.22-2.103 2.415-4.298 2.415-2.466 0-3.6-1.35-4.303-2.66l11.763-4.88-.6-1.43c-1.136-2.8-3.787-5.14-7.295-5.14zm.153 3.374c1.603 0 2.756.852 3.246 1.874l-7.856 3.283c-.34-2.542 2.07-5.157 4.6-5.157z" fill="#db3236"/><path d="M91.6 40.787h3.864V14.93H91.6z" fill="#3cba54"/><defs><path id="A" d="M42.634 23.755c-5.138 0-8.82 4.017-8.82 8.7 0 4.754 3.57 8.845 8.88 8.845 4.806 0 8.743-3.673 8.743-8.743 0-5.8-4.58-8.803-8.803-8.803zm.05 3.446c2.526 0 4.92 2.043 4.92 5.334 0 3.22-2.384 5.322-4.932 5.322-2.8 0-5-2.242-5-5.348 0-3.04 2.18-5.308 5.02-5.308z"/></defs></svg> GenAI
    </div>
""", unsafe_allow_html=True)

@st.cache_data
def get_data() -> pd.DataFrame:
    return run_query("""
      MATCH (n:Episode) return n.episode as Episode, 
      n.title as Title, n.synopsis as Synopsis,
      n.img as Image, n.id as Id, n.videoUrl as Url ORDER BY Id""")

df_episodes = get_data()

placeholder = st.empty()

with placeholder.container():
        df_players = run_query("""MATCH (n:Player) return n.name as name""")
        df_teams = run_query("""MATCH (n:Team) return n.name as name""")

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(
            label="Episodes",
            value=df_episodes['Id'].size
        )     
        kpi2.metric(
            label="Teams",
            value=df_teams.size
        )
        kpi3.metric(
            label="Players",
            value=df_players.size
        )
    
        ep_team_col = st.columns(1)
        st.markdown("### Episodes & Team mentions")
        df_te_1 = run_query("""
            MATCH (e:Episode) 
            return e.id as id, 'Episode '+e.episode as label, '#33a02c' as color""")
        df_te_2 = run_query("""
            MATCH (t:Team) 
            return t.id as id, t.name as label, '#1f78b4' as color""")
        df_te_3 = run_query("""
            MATCH (t:Player) 
            return t.id as id, t.name as label, '#fdbf6f' as color""")
        df_te = pd.concat([df_te_1, df_te_2], ignore_index=True)
        df_te = pd.concat([df_te, df_te_3], ignore_index=True)
        df_teams_episodes_1 = run_query("""
            MATCH (e:Episode)-[d:DISCUSSES_TEAM]->(t:Team)
            return e.id as source, t.id as target, count(*) as value, 
                '#a6cee3' as link_color ORDER BY value DESC""")
        df_teams_episodes_2 = run_query("""
            MATCH (e:Episode)-[:DISCUSSES_PLAYER]->(p:Player)-[:PART_OF]->(t:Team)
            return t.id as source, p.id as target, count(*) as value, 
                '#fdbf6f' as link_color ORDER BY value DESC LIMIT 15""")
        df_teams_episodes = pd.concat([df_teams_episodes_1, df_teams_episodes_2], ignore_index=True)
        label_mapping = dict(zip(df_te['id'], df_te.index))
        df_teams_episodes['src_id'] = df_teams_episodes['source'].map(label_mapping)
        df_teams_episodes['target_id'] = df_teams_episodes['target'].map(label_mapping)
        
        sankey = go.Figure(data=[go.Sankey(
            arrangement="snap",
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(
                    color = "black",
                    width = 0.4
                ),
                label = df_te['label'].values.tolist(),
                color = df_te['color'].values.tolist(),
                ),
            link = dict(
                source = df_teams_episodes['src_id'].values.tolist(),
                target = df_teams_episodes['target_id'].values.tolist(),
                value = df_teams_episodes['value'].values.tolist(),
                color = df_teams_episodes['link_color'].values.tolist()
            )
        )])
        st.plotly_chart(sankey, use_container_width=True)

        team_col = st.columns(1)
        st.markdown("### Popular Teams")
        df_teams = run_query("""
            MATCH (e:Episode)-[:DISCUSSES_TEAM]->(p:Team) 
            return DISTINCT p.name as team, count(e) as episodes
            ORDER BY episodes DESC LIMIT 10""")
        size_max_default = 7
        scaling_factor = 5
        fig_team = px.scatter(df_teams, x="team", y="episodes",
                    size="episodes", color="team",
                        hover_name="team", log_y=True, 
                        size_max=size_max_default*scaling_factor)
        st.plotly_chart(fig_team, use_container_width=True)

        # create two columns for charts
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown("### Most talked about Players")
            df = run_query("""
              MATCH (e:Episode)-[:DISCUSSES_PLAYER]->(p:Player) 
              return DISTINCT p.name as player, count(e) as episodes
              ORDER BY episodes DESC LIMIT 10""")
            fig = px.scatter(df, x="player", y="episodes",
                      size="episodes", color="player",
                            hover_name="player", log_y=True, 
                            size_max=size_max_default*scaling_factor)
            st.plotly_chart(fig, use_container_width=True)
            
        with fig_col2:
            st.markdown("### Most talked about Coaches")
            df = run_query("""
              MATCH (e:Episode)-[:DISCUSSES_COACH]->(p:Coach) 
              return p.name as coach, count(e) as episodes
              ORDER BY episodes DESC LIMIT 10""")
            fig2 = px.scatter(df, x="coach", y="episodes",
                      size="episodes", color="coach",
                            hover_name="coach", log_y=True, 
                            size_max=size_max_default*scaling_factor)
            st.plotly_chart(fig2, use_container_width=True)
        