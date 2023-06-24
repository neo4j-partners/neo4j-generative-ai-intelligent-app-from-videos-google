import time

import numpy as np 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from neo4j_driver import run_query

st.set_page_config(
    page_title="AFL Access All Areas",
    page_icon="🧠",
    layout="wide",
)

st.title("AFL Access All Areas")

# @st.cache_data
def get_data() -> pd.DataFrame:
    return run_query("""
      MATCH (n:Episode) return n.id as Id, 
      n.title as Title, n.synopsis as Synopsis,
      n.img as Image, n.videoUrl as Url""")

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
            return e.id as id, e.title as label, '#33a02c' as color""")
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
        
        st.markdown("### Episodes")
        st.dataframe(df_episodes)