import vertexai
import streamlit as st
from vertexai.preview.language_models import TextGenerationModel
from vertexai.preview.language_models import CodeGenerationModel
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import traceback

project_id = st.secrets["GCP_PROJECT"]
location = st.secrets["GCP_LOCATION"]

vertexai.init(project=project_id, location=location)

def run_text_model(
    project_id: str,
    model_name: str,
    temperature: float,
    max_decode_steps: int,
    top_p: float,
    top_k: int,
    prompt: str,
    location: str = "us-central1",
    tuned_model_name: str = "",
    ) :
    """Text Completion Use a Large Language Model."""
    vertexai.init(project=project_id, location=location)
    model = TextGenerationModel.from_pretrained(model_name)
    if tuned_model_name:
      model = model.get_tuned_model(tuned_model_name)
    response = model.predict(
        prompt,
        temperature=temperature,
        max_output_tokens=max_decode_steps,
        top_k=top_k,
        top_p=top_p,)
    return response.text

def prompt_text_bison(prompt, tuned_model_name=''):
    try:
        res = run_text_model(project_id, "text-bison@001", 0, 1024, 0.8, 40, prompt, location, tuned_model_name)
        return res
    except Exception as e:
        traceback.print_exc()
        print(e)

def prompt_code_bison(prompt):
    try:
        parameters = {
            "temperature": 0,
            "max_output_tokens": 2048
        }
        model = CodeGenerationModel.from_pretrained("code-bison@001")
        res = model.predict(
            prefix = prompt,
            **parameters
        )
        return res.text
    except Exception as e:
        traceback.print_exc()
        print(e)

