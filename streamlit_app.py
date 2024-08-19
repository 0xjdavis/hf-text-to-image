import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Setting page layout
st.set_page_config(
    page_title="Hugging Face Text-to-Image Generation",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.header("About App")
st.sidebar.markdown('This is a text-to-image generation app using Hugging Face models.')

# Model selection
model_options = {
    "Midjourney v6": "Kvikontent/midjourney-v6",
    "FLUX.1-schnell": "black-forest-labs/FLUX.1-schnell"
}
selected_model = st.sidebar.selectbox("Select Model", list(model_options.keys()))

# Main content
st.title("Hugging Face Text-to-Image Generation")
st.caption("Prompted artwork powered by Hugging Face Models")

# Input for Hugging Face API Token
hf_api_key = st.text_input("Enter your Hugging Face API Token", type="password")

# Text input for the prompt
prompt = st.text_input("Enter your prompt for image generation")

if st.button("Generate Image"):
    if not hf_api_key:
        st.error("Please enter your Hugging Face API Token.")
    elif not prompt:
        st.error("Please enter a prompt for image generation.")
    else:
        # API call to Hugging Face
        API_URL = f"https://api-inference.huggingface.co/models/{model_options[selected_model]}"
        headers = {"Authorization": f"Bearer {hf_api_key}"}

        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.content

        image_bytes = query({
            "inputs": prompt,
        })

        # Display the generated image
        if image_bytes.startswith(b'{"error'):
            st.error("An error occurred during image generation. Please try again.")
        else:
            image = Image.open(BytesIO(image_bytes))
            st.image(image, caption="Generated Image")

            # Download button
            buf = BytesIO()
            image.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.download_button(
                label="Download Image",
                data=byte_im,
                file_name="generated_image.png",
                mime="image/png"
            )

# Copyright
st.sidebar.caption("©️ Copyright 2024 Your Name")
