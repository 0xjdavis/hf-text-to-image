import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Setting page layout
st.set_page_config(
    page_title="Midjourney v6 Text-to-Image Generation",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.sidebar.header("About App")
st.sidebar.markdown('This is a zero-shot text-to-image generation chatbot using Midjourney v6 model by <a href="https://ai.jdavis.xyz" target="_blank">0xjdavis</a>.', unsafe_allow_html=True)

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

st.title("Midjourney v6 Text-to-Image Generation")
st.write("Prompted artwork powered by Midjourney v6 Model")

# Hugging Face API
API_URL = "https://api-inference.huggingface.co/models/Kvikontent/midjourney-v6"
headers = {"Authorization": f"Bearer {st.secrets['huggingface_key']}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

# ---------------------------------------------- 
# CTA BUTTON
if "messages" in st.session_state:
    url = "/Midjourney%20Text%20To%20Image%20Generation"
    st.markdown(
        f'<div><a href="{url}" target="_self" style="justify-content:center; padding: 10px 10px; background-color: #2D2D2D; color: #efefef; text-align: center; text-decoration: none; font-size: 16px; border-radius: 8px;">Clear History</a></div><br /><br />',
        unsafe_allow_html=True
    )

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "I am feeling creative today! What would you like to generate an image of?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if "huggingface_key" not in st.secrets:
        st.info("Please add your Hugging Face API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # ----------------------------------------------
    # GENERATE IMAGE
    with st.spinner("Generating image..."):
        image_bytes = query({
            "inputs": prompt,
        })

    if image_bytes:
        image = Image.open(BytesIO(image_bytes))
        st.image(image, caption=prompt)

        with st.expander("Download Image"):
            # ----------------------------------------------
            # DOWNLOAD BUTTON
            buf = BytesIO()
            image.save(buf, format="PNG")
            byte_image = buf.getvalue()

            btn = st.download_button(
                label="Download Image",
                data=byte_image,
                file_name="midjourney_image.png",
                mime="image/png",
            )
    else:
        st.error("Failed to generate image. Please try again.")

    st.session_state.messages.append({"role": "assistant", "content": "Here's the image I generated based on your prompt. What do you think?"})
