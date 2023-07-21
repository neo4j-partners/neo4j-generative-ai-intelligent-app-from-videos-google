from string import Template
import time
import ingestion.vertexai_util as vertexai_util
import ingestion.prompts as prompts
import ingestion.webvtt_util as wu
import re
import numpy as np
from pathlib import Path
from timeit import default_timer as timer
from graphdatascience import GraphDataScience
import traceback

import streamlit as st

host = st.secrets["NEO4J_HOST"]+":"+st.secrets["NEO4J_PORT"]
user = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASSWORD"]
db = st.secrets["NEO4J_DB"]

gds = GraphDataScience(
    st.secrets["NEO4J_HOST"],
    auth=(user, password),
    aura_ds=True)

gds.set_database("neo4j")

def run_pipeline(transcript_url, episode_num, video_url, title, img):
    start = timer()
    try:
        f = transcript_url
        episode_id = Path(f).stem
        print(f"  {episode_id}: Reading Transcript")
        transcript = wu.vtt_to_json(f, True, False)
        whole_transcript = ''
        for t in transcript:
            whole_transcript = whole_transcript + ' ' + t['lines']
        whole_transcript = whole_transcript.strip()
        print(f"    {episode_id}: Extracting Entities & Relationships")
        results = run_extraction(episode_id, whole_transcript)
        st.toast("Entity Extraction ✅")
        print(f"    {episode_id}: Generating Cypher")
        ent_cyp, rel_cyp = generate_cypher(episode_id, results)
        st.toast("Cypher Generation ✅")
        print(f"    {episode_id}: Ingesting Entities")
        for e in ent_cyp:
            gds.run_cypher(e)
        st.toast("Entities Saved to Neo4j ✅")
        print(f"    {episode_id}: Ingesting Relationships")
        for r in rel_cyp:
            gds.run_cypher(r)
        st.toast("Relationships Saved to Neo4j ✅")
        gds.run_cypher(f"""
            MATCH (n:Episode)
            WHERE n.id = '{episode_id}'
            SET n.videoUrl = '{video_url}',
                n.title = "{title}",
                n.img = '{img}',
                n.episode = '{episode_num}'
            RETURN n
        """)
        st.toast("Metadata Saved to Neo4j ✅")
        print(f"    {episode_id}: Disambiguating Teams")
        disambiguate_teams()
        df_teams = gds.run_cypher('MATCH (n:Team) WHERE NOT(n.name CONTAINS "[") OR NOT(toLower(n.name) CONTAINS "football club") RETURN n.name as name')
        if(len(df_teams) > 0) :
            disambiguate_teams(df_teams)
        st.toast("Team Name Disambiguation ✅")
        print(f"    {episode_id}: Disambiguating Players")
        disambiguate_players()
        st.toast("Player Name Disambiguation ✅")
        print(f"    {episode_id}: Processing DONE")
        return [ent_cyp, rel_cyp]
    except Exception as e:
        traceback.print_exc()
        print(f"    {episode_id}: Processing Failed with exception {e}")
        return None
    finally:
        end = timer()
        elapsed = (end-start)
        print(f"    {f}: Took {elapsed}secs")

def run_extraction(episode_id, whole_transcript):
    start = timer()
    results = {"entities": [], "relationships": []}

    #Extract Episode
    extract_episode(episode_id, whole_transcript, results)
    st.toast("Generated Summary ✅")

    #Extract Headline
    extract_headline(whole_transcript, results)
    st.toast("Generated Headlines ✅")

    #Extract Theme
    extract_theme(whole_transcript, results)
    st.toast("Generated Themes ✅")

    #Extract Players & their Teams
    extract_player_team(whole_transcript, results)
    st.toast("Extracted Players & Teams ✅")

    #Extract Coaches & their Teams
    extract_coach_team(whole_transcript, results)
    st.toast("Extracted Coaches & Teams ✅")

    #Extract Predictions & Predictors
    extract_predictions(whole_transcript, results)
    st.toast("Extracted Predictions ✅")

    link_entities(results)
    end = timer()
    elapsed = (end-start)
    print(f"    {episode_id}: Entity Extraction took {elapsed}secs")
    return [results]

def get_cypher_compliant_var(_id):
    s = "_"+ re.sub(r'[\W_]', '', _id).lower() #avoid numbers appearing as firstchar; replace spaces
    return s[:20] #restrict variable size

def extract_episode(episode_id, text, results):
    _prompt = Template(prompts.episode_prompt_tpl).substitute(ctext=text)
    summary = vertexai_util.prompt_code_bison(_prompt) or ""
    if 'Answer:\n' in summary:
        summary = summary.split('Answer:\n ')[1]
    results["entities"].append({"label": "Episode", "id": str(episode_id), "synopsis": summary})
    return results

def extract_headline(text, results):
    _prompt = Template(prompts.headline_prompt_tpl).substitute(ctext=text)
    _extraction = vertexai_util.prompt_text_bison(_prompt) or ""
    i = 0
    if '- ' in _extraction:
        for h in _extraction.split('- ')[1:]:
            i += 1
            headline_id = "h_"+str(round(time.time() * 1000)+i)
            results["entities"].append({"label": "Headline", "id": headline_id, "name": h.strip()})
    else:
        headline_id = "h_"+str(round(time.time() * 1000)+i)
        results["entities"].append({"label": "Headline", "id": headline_id, "name": _extraction.strip()})
    return results

def extract_theme(text, results):
    _prompt = Template(prompts.theme_prompt_tpl).substitute(ctext=text)
    _extraction = vertexai_util.prompt_code_bison(_prompt) or ""
    i = 0
    if '- ' in _extraction:
        for h in _extraction.split('- ')[1:]:
            i += 1
            results["entities"].append({"label": "Theme", "id": get_cypher_compliant_var(h.strip()), "name": h.strip()})
    else:
        results["entities"].append({"label": "Theme", "id": get_cypher_compliant_var(_extraction.strip()), "name": _extraction.strip()})
    return results

def extract_player_team(text, results):
    player_team_set = set()
    team_dict = {}
    i = 0
    text_arr = text.split('.')
    CHUNK_SIZE = 5
    for chunk in np.array_split(text_arr, CHUNK_SIZE):
        _prompt = Template(prompts.player_prompt_tpl).substitute(ctext=".".join(chunk))
        _extraction = vertexai_util.prompt_text_bison(_prompt)
        for t in _extraction.split('\n'):
           tmp = t.lstrip('(').rstrip(')').split(',')
           if not t.startswith('(') or len(tmp) < 2:
            continue
           player = tmp[0].strip()
           team = tmp[1].strip()
           if not player.startswith('player') and not team.startswith(player): #sometimes player and team name gets confused
               player_team_set.add((player, team))
    for (player, team) in player_team_set:
        i += 1
        player_id = get_cypher_compliant_var(player)
        results["entities"].append({"label": "Player", "id": player_id, "name": player})
        if team != 'None':
            if team not in team_dict:
                _id = get_cypher_compliant_var(team)
                results["entities"].append({"label": "Team", "id": _id, "name": team})
                team_dict[team] = _id
            results["relationships"].append(f"{player_id}|PART_OF|{team_dict[team]}")
    return results

def extract_coach_team(text, results):
    coach_team_set = set()
    team_dict = {}
    i = 0
    text_arr = text.split('.')
    CHUNK_SIZE = 5
    for chunk in np.array_split(text_arr, CHUNK_SIZE):
        _prompt = Template(prompts.coach_prompt_tpl).substitute(ctext=".".join(chunk))
        _extraction = vertexai_util.prompt_text_bison(_prompt)
        for t in _extraction.split('\n'):
           tmp = t.lstrip('(').rstrip(')').split(',')
           if not t.startswith('(') or len(tmp) < 2:
            continue
           coach = tmp[0].strip()
           team = tmp[1].strip()
           if not coach.startswith('coach') and not team.startswith(coach): #sometimes coach and team name gets confused
               coach_team_set.add((coach, team))
    for (coach, team) in coach_team_set:
        i += 1
        coach_id = get_cypher_compliant_var(coach)
        results["entities"].append({"label": "Coach", "id": coach_id, "name": coach})
        if 'None' != team:
            if team not in team_dict:
                _id = get_cypher_compliant_var(team)
                results["entities"].append({"label": "Team", "id": _id, "name": team})
                team_dict[team] = _id
            results["relationships"].append(f"{coach_id}|COACH_OF|{team_dict[team]}")
    return results

def extract_predictions(text, results):
    _prompt = Template(prompts.predictions_prompt_tpl).substitute(ctext=text)
    _extraction = vertexai_util.prompt_code_bison(_prompt) or ""
    i = 0
    pred_dict = {}
    if '- ' in _extraction:
        for h in _extraction.split('- ')[1:]:
            i += 1
            pred = h.strip().lstrip('prediction:').strip()
            if pred not in pred_dict:
                results["entities"].append({"label": "Prediction", "id": 'pred'+str(round(time.time() * 1000)+i), "name": pred})
                pred_dict[pred] = True
    else:
        results["entities"].append({"label": "Prediction", "id": 'pred'+str(round(time.time() * 1000)+i), "name": _extraction})
    return results

def link_entities(results):
    episode_id = results["entities"][0]["id"]
    for e in results["entities"][1:]:
        if e['label'] == 'Headline':
            results["relationships"].append(f"{episode_id}|HAS_HEADLINE|{e['id']}")
        if e['label'] == 'Theme':
            results["relationships"].append(f"{episode_id}|HAS_THEME|{e['id']}")
        if e['label'] == 'Team':
            results["relationships"].append(f"{episode_id}|DISCUSSES_TEAM|{e['id']}")
        if e['label'] == 'Player':
            results["relationships"].append(f"{episode_id}|DISCUSSES_PLAYER|{e['id']}")
        if e['label'] == 'Coach':
            results["relationships"].append(f"{episode_id}|DISCUSSES_COACH|{e['id']}")
        if e['label'] == 'Prediction':
            results["relationships"].append(f"{episode_id}|HAS_PREDICTION|{e['id']}")
    return results

def get_prop_str(prop_dict, _id):
    s = []
    for key, val in prop_dict.items():
      if key != 'label' and key != 'id':
         s.append(_id+"."+key+' = "'+str(val).replace('\"', '"').replace('"', '\"')+'"') 
    return ' ON CREATE SET ' + ','.join(s)

def generate_cypher(file_name, in_json):
    e_map = {}
    e_stmt = []
    r_stmt = []
    e_stmt_tpl = Template("($id:$label{id:'$key'})")
    e_stmt_tpl_1 = Template("($id:$label{name:toLower('$name')})")
    r_stmt_tpl = Template("""
      MATCH $src
      MATCH $tgt
      MERGE ($src_id)-[:$rel]->($tgt_id)
    """)
    for obj in in_json:
      for j in obj['entities']:
          props = ''
          label = j['label']
          id = ''
          if label == 'Episode':
            id = file_name
          else:
            id = j['id']
          if label in ['Episode', 'Headline', 'Theme', 'Prediction', 'Player', 'Coach', 'Team']:
            varname = get_cypher_compliant_var(j['id'])
            stmt = e_stmt_tpl.substitute(id=varname, label=label, key=id)
            e_map[varname] = stmt
            e_stmt.append('MERGE '+ stmt + get_prop_str(j, varname))

      for st in obj['relationships']:
          rels = st.split("|")
          src_id = get_cypher_compliant_var(rels[0].strip())
          rel = rels[1].strip()
          if rel in ['HAS_HEADLINE', 'HAS_THEME', 'DISCUSSES_TEAM', 'DISCUSSES_PLAYER', \
                     'PART_OF', 'DISCUSSES_COACH', 'COACH_OF', 'HAS_PREDICTION']: #we ignore other relationships
            tgt_id = get_cypher_compliant_var(rels[2].strip())
            stmt = r_stmt_tpl.substitute(
              src_id=src_id, tgt_id=tgt_id, src=e_map[src_id], tgt=e_map[tgt_id], rel=rel)
            r_stmt.append(stmt)

    return e_stmt, r_stmt


def disambiguate_teams(df_teams = gds.run_cypher('MATCH (n:Team) RETURN n.name as name')):
    entity_disambiguation_prompt_tpl = """Here is the list of Australian Football League Teams extracted from an NLP pipeline. 
Now, disambiguate each of the Teams as tuples like (1 tuple per line):
(ambiguous_team_name, correct_official_name [correct_nick_name])
`West Coast Eagles` and `West Coast Football Club` are the same team. So disambiguate them to one - `West Coast Football Club [Eagles]`

Ambiguous AFL Team names list:
$ctext
Disambiguated names list:
"""
    _prompt = Template(entity_disambiguation_prompt_tpl).substitute(ctext='\n'.join(df_teams['name']))
    _extraction = vertexai_util.prompt_text_bison(_prompt)
    for line in _extraction.split('\n'):
        tmp = line.lstrip('(').rstrip(')').split(',')
        if not line.startswith('(') or len(tmp) < 2:
            continue
        amb_name = tmp[0].strip()
        full_name = tmp[1].strip()
        # print(f"{amb_name} | {full_name}")
        if len(amb_name) > 0 and amb_name != 'None':
            gds.run_cypher(f"""
                MATCH (n:Team) 
                WHERE toLower(n.name) = "{amb_name.lower()}"
                SET n.name = "{full_name}"
                RETURN n.name"""
            )
    gds.run_cypher("""MATCH (n:Team)
        WITH n.name as name, COLLECT(n) AS ns
        WHERE size(ns) > 1
        CALL apoc.refactor.mergeNodes(ns) YIELD node
        RETURN node.id, node.name""")
    print(gds.run_cypher('MATCH (n:Team) RETURN n.name as name'))


def disambiguate_players():
    df_players = gds.run_cypher('MATCH (n:Player)-[:PART_OF]->(t:Team) SET n.name = trim(n.name) RETURN DISTINCT n.name as player, t.name as team')
    player_disambiguation_prompt_tpl = """Here are the list of Australian Football League Players and their names extracted from an NLP pipeline. 
Now, disambiguate them and provide the official and nicknames for each of the Players as tuples like:
(ambiguous_player_name, official_player_name [nick_name_of_the_player])

Ambiguous AFL player & team names Format: (player, team):
$ctext
Disambiguated names:
"""
    for df_split in np.array_split(df_players, 6):
        _prompt = Template(player_disambiguation_prompt_tpl).substitute(ctext='\n'.join(df_split['player']+', '+df_split['team']))
        _extraction = vertexai_util.prompt_text_bison(_prompt)
        for line in _extraction.split('\n'):
            tmp = line.lstrip('(').rstrip(')').split(',')
            if not line.startswith('(') or len(tmp) < 2:
                continue
            amb_name = tmp[0]
            correct_name = tmp[1]
            if len(amb_name) > 0 and len(correct_name) > 0 and amb_name != 'None' and correct_name != 'None':
                gds.run_cypher(f"""
                    MATCH (n:Player) 
                    WHERE toLower(n.name) = "{amb_name.lower()}"
                    SET n.name = "{correct_name}"
                    RETURN n.name"""
                )

    gds.run_cypher("""MATCH (n:Player)
    WITH n.name as name, COLLECT(n) AS ns
    WHERE size(ns) > 1
    CALL apoc.refactor.mergeNodes(ns) YIELD node
    RETURN node.id, node.name""")

