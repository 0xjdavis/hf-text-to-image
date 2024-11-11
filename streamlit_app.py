import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64
import json
import time

# Setting page layout
st.set_page_config(
    page_title="Hugging Face Text-to-Image Generation",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Secrets
huggingface_api_key = st.secrets["huggingface_key"]
api_key_input = '1'

# API Key Input
if 'huggingface_api_key' not in st.session_state:
    st.session_state.huggingface_api_key = '',
    st.session_state.huggingface_api_key = api_key_input


# Sidebar
st.sidebar.header("About App")
st.sidebar.markdown('This is a zero-shot text-to-image generation chatbot using Hugging Face models by <a href="https://ai.jdavis.xyz" target="_blank">0xjdavis</a>.', unsafe_allow_html=True)

# Model selection
model_options = {
    "Midjourney v6": "Kvikontent/midjourney-v6",
    "FLUX.1 [schnell]": "black-forest-labs/FLUX.1-schnell",
    "FLUX.1 [dev]": "black-forest-labs/FLUX.1-dev",
    "OpenJourney": "prompthero/openjourney",
    "Stable Diffusion 2.1": "stabilityai/stable-diffusion-2-1",
    "Stable Diffusion XL": "stabilityai/stable-diffusion-xl-base-1.0",
    "Stable Diffusion 1.5": "runwayml/stable-diffusion-v1-5"
}
selected_model = st.sidebar.selectbox("Select Model", list(model_options.keys()))

# Calendly
st.sidebar.markdown("""
    <hr />
    <center>
    <div style="border-radius:8px;padding:8px;background:#fff";width:100%;">
    <img src="https://avatars.githubusercontent.com/u/98430977" alt="Oxjdavis" height="100" width="100" border="0" style="border-radius:50%"/>
    <br />
    <span style="height:12px;width:12px;background-color:#77e0b5;border-radius:50%;display:inline-block;"></span> <b style="color:#000000">I'm available for new projects!</b><br />
    <a href="https://calendly.com/0xjdavis" target="_blank"><button style="background:#126ff3;color:#fff;border: 1px #126ff3 solid;border-radius:8px;padding:8px 16px;margin:10px 0">Schedule a call</button></a><br />
    </div>
    </center>
    <br />
""", unsafe_allow_html=True)

# Copyright
st.sidebar.caption("©️ Copyright 2024 J. Davis")

st.title("Hugging Face Text-to-Image Generation")
st.write(f"Prompted artwork powered by {selected_model} Model")

# Session state initialization
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "I am feeling creative today! What would you like to generate an image of?"}]

# Display messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

def is_json(content):
    """Check if content is JSON by attempting to parse it"""
    try:
        if isinstance(content, bytes):
            json.loads(content.decode('utf-8'))
        else:
            json.loads(content)
        return True
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False

def query_with_retry(API_URL, headers, payload, max_retries=5, initial_wait=2):
    """
    Query the API with retry mechanism for handling model loading states
    """
    status_placeholder = st.empty()
    
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            
            # First, check if the response is JSON (error message)
            if is_json(response.content):
                error_json = json.loads(response.content.decode('utf-8'))
                if "error" in error_json:
                    if "loading" in error_json["error"].lower():
                        wait_time = initial_wait * (2 ** attempt)
                        status_placeholder.info(f"Model is loading. Waiting {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(error_json["error"])
            else:
                # If it's not JSON, it should be image data
                try:
                    # Verify it's a valid image
                    Image.open(BytesIO(response.content))
                    status_placeholder.empty()
                    return response.content
                except Exception as e:
                    raise Exception(f"Invalid image data received: {str(e)}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
            
    raise Exception("Max retries reached. Model is still loading.")

if prompt := st.chat_input():
    if not huggingface_api_key:
        st.info("Please add your Hugging Face API key to continue.")
        st.stop()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # GENERATE IMAGE
    API_URL = f"https://api-inference.huggingface.co/models/{model_options[selected_model]}"
    headers = {"Authorization": f"Bearer {huggingface_api_key}"}
    
    try:
        # Show generating status
        status_message = st.info("Generating image...", icon="🎨")
        
        # Query with retry mechanism
        image_bytes = query_with_retry(API_URL, headers, {"inputs": prompt})
        
        # Clear the generating status
        status_message.empty()
        
        # Create image from bytes
        image = Image.open(BytesIO(image_bytes))
        
        # Display the image
        st.image(image, caption="Generated Image")
        
        # Show download and details in a tab layout instead of nested expanders
        tab1, tab2 = st.tabs(["Download", "Image Details"])
        
        with tab1:
            # DOWNLOAD BUTTON
            st.download_button(
                label="Download Image",
                data=image_bytes,
                file_name="generated_image.png",
                mime="image/png",
            )
        
        with tab2:
            # Display base64 encoded image for debugging
            st.text("Base64 Encoded Image:")
            st.text(base64.b64encode(image_bytes).decode())
        
        # Show success message
        st.success("Image generated successfully!")
    
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        if "Max retries reached" in str(e):
            st.info("The model is taking longer than expected to load. Please try again in a few minutes.")