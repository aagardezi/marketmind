from google import genai
from google.genai import types
import base64
import helpercode
import streamlit as st



PROJECT_ID = helpercode.get_project_id()
LOCATION = "us-central1"

def shareprice(params):
  client = genai.Client(
      vertexai=True,
      project=PROJECT_ID,
      location=LOCATION,
  )


  model = st.session_state.modelname
  contents = [
    types.Content(
      role="user",
      parts=[
        types.Part.from_text(text=f"""What is the current share price for {params['symbol']}""")
      ]
    )
  ]
  tools = [
    types.Tool(google_search=types.GoogleSearch())
  ]
  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 8192,
    response_modalities = ["TEXT"],
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
    tools = tools,
    system_instruction=[types.Part.from_text(text="""Only give a one line response with the share price""")],
  )

  response =client.models.generate_content(
    model = model,
    contents = contents,
    config = generate_content_config)
  
  return {'share price': response.candidates[0].content.parts[0].text}


function_handler = {
    "shareprice": shareprice,
}