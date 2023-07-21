import streamlit as st
import ingestion.pipeline as ingestion

st.set_page_config(
    page_title="AFL Access All Areas - Data Ingestion",
    page_icon="🧠",
    layout="wide",
)

st.title("AFL Access All Areas - Data Ingestion")

with st.form("ingestion_form"):
   video_url = st.text_input('Video URL', 'https://www.afl.com.au/ondemand/shows/490977/access-all-areas?episode=11#2023')
   transcript_url = st.text_input('Video Transcript URL', 'https://afl-cc-001-uptls.akamaized.net/afl_6327986707112_20230522T001659Z/afl_6327986707112_20230522T001659Z.vtt')
   title = st.text_input('Transcript Title', 'Episode 11')
   img = st.text_input('Thumbnail Image', 'http://bpvms-img-001-uptls.akamaized.net/web/images/20230529102516a_1024x576.jpg')
   episode_num = st.text_input('Episode Number', 11)

   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")
   if submitted:
       with st.spinner('Processing the Transcript...'):
          res = ingestion.run_pipeline(transcript_url, episode_num, video_url, title, img)
       if res is not None:
          st.success('Done!')
          with st.expander("See Generated Cypher"):
              st.markdown(f"""
                          ```
                          {res}
                          ```
              """)
       else:
          st.error("Transcription could not be ingested now. Try again later.")