import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from diffusers import DiffusionPipeline
import torch

# Setting page layout
st.set_page_config(
    page_title="AI Text-to-Image Generation",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.header("About App")
st.sidebar.markdown('This is a zero-shot text-to-image generation chatbot using various AI models by <a href="https://ai.jdavis.xyz" target="_blank">0xjdavis</a>.', unsafe_allow_html=True)

# Model selection dropdown
model_option = st.sidebar.selectbox(
    "Select Model",
    ("Midjourney v6", "FLUX.1-schnell")
)

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

st.title("AI Text-to-Image Generation")
st.caption(f"Prompted artwork powered by {model_option} Model")

# CTA BUTTON
if "messages" in st.session_state:
    url = "/AI%20Text%20To%20Image%20Generation"
    st.markdown(
        f'<div><a href="{url}" target="_self" style="justify-content:center; padding: 10px 10px; background-color: #2D2D2D; color: #efefef; text-align: center; text-decoration: none; font-size: 16px; border-radius: 8px;">Clear History</a></div><br /><br />',
        unsafe_allow_html=True
    )

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "I am feeling creative today! What would you like to generate an image of?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Load the selected model
@st.cache_resource
def load_model(model_name):
    if model_name == "Midjourney v6":
        return DiffusionPipeline.from_pretrained("Kvikontent/midjourney-v6", torch_dtype=torch.float16).to("cuda")
    elif model_name == "FLUX.1-schnell":
        return DiffusionPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.float16).to("cuda")

model = load_model(model_option)

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Generate image
    with st.spinner("Generating image..."):
        image = model(prompt).images[0]

    # Display the generated image
    st.image(image)

    with st.expander("View Image Details"):
        # Convert PIL Image to bytes
        buf = BytesIO()
        image.save(buf, format="PNG")
        byte_image = buf.getvalue()

        # Download button
        btn = st.download_button(
            label="Download Image",
            data=byte_image,
            file_name="generated_image.png",
            mime="image/png",
        )

    # Add the assistant's response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": "Here's the image I generated based on your prompt. What do you think?"})
