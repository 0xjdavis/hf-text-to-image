import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64

# Setting page layout
st.set_page_config(
    page_title="Hugging Face Text-to-Image Generation",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Secrets
huggingface_api_key = st.secrets["huggingface_key"]

# Sidebar
st.sidebar.header("About App")
st.sidebar.markdown('This is a zero-shot text-to-image generation chatbot using Hugging Face models by <a href="https://ai.jdavis.xyz" target="_blank">0xjdavis</a>.', unsafe_allow_html=True)

# Model selection
model_options = {
    "Midjourney v6": "Kvikontent/midjourney-v6",
    "FLUX.1-schnell": "black-forest-labs/FLUX.1-schnell"
}
selected_model = st.sidebar.selectbox("Select Model", list(model_options.keys()))

# Calendly
st.sidebar.markdown("""
    <hr />
    <center>
    <div style="border-radius:8px;padding:8px;background:#fff";width:100%;">
    <img src="https://avatars.githubusercontent.com/u/98430977" alt="Oxjdavis" height="100" width="100" border="0" style="border-radius:50%"/>
    <br />
    <span style="height:12px;width:12px;background-color:#77e0b5;border-radius:50%;display:inline-block;"></span> <b>I'm available for new projects!</b><br />
    <a href="https://calendly.com/0xjdavis" target="_blank"><button style="background:#126ff3;color:#fff;border: 1px #126ff3 solid;border-radius:8px;padding:8px 16px;margin:10px 0">Schedule a call</button></a><br />
    </div>
    </center>
    <br />
""", unsafe_allow_html=True)

# Copyright
st.sidebar.caption("©️ Copyright 2024 J. Davis")

st.title("Hugging Face Text-to-Image Generation")
st.write(f"Prompted artwork powered by {selected_model} Model")

# CTA BUTTON
if "messages" in st.session_state:
    url = "https://hf-text-image.streamlit.app"
    st.markdown(
        f'<div><a href="{url}" target="_self" style="justify-content:center; padding: 10px 10px; background-color: #2D2D2D; color: #efefef; text-align: center; text-decoration: none; font-size: 16px; border-radius: 8px;">Clear History</a></div><br /><br />',
        unsafe_allow_html=True
    )

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "I am feeling creative today! What would you like to generate an image of?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not huggingface_api_key:
        st.info("Please add your Hugging Face API key to continue.")
        st.stop()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # GENERATE IMAGE
    API_URL = f"https://api-inference.huggingface.co/models/{model_options[selected_model]}"
    headers = {"Authorization": f"Bearer {huggingface_api_key}"}
    
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.content
    
    image_bytes = query({
        "inputs": prompt,
    })
    
    try:
        # Display the image
        image = Image.open(BytesIO(image_bytes))
        st.image(image, caption="Generated Image")
        
        with st.expander("View Image Details"):
            # DOWNLOAD BUTTON
            btn = st.download_button(
                label="Download Image",
                data=image_bytes,
                file_name="generated_image.png",
                mime="image/png",
            )
            
            # Display base64 encoded image for debugging
            st.text("Base64 Encoded Image:")
            st.text(base64.b64encode(image_bytes).decode())
    
    except Exception as e:
        st.error(f"An error occurred while processing the image: {str(e)}")
        st.error("The API might have returned an error message instead of an image. Here's the raw response:")
        st.text(image_bytes.decode('utf-8', errors='replace'))
