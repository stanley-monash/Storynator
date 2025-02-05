# Imports
from openai import OpenAI
import streamlit as st
from text_translation import extract_text_from_image, translate_text
from cards import travel_packages_tab
import os
import googlemaps
from itertools import permutations
from urllib.parse import quote
import requests
import folium

# Secrets stuff
api_key = st.secrets['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["PersonaTour Guide", "Image Translation", "Tours", "Route Finder"])

with tab1:
    # Chatbot main
    st.title("PersonaTour guide")

    # Set a default model
    if "openai_model" not in st.session_state:
        # assigns value gpt-3.5-turbo to key openai_model in the session state dictionary
        st.session_state["openai_model"] = "gpt-4"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # # Make assistant send a greeting
    # with st.chat_message("assistant"):
    #     st.write_stream("Hi there! I am your personal travel guide that will help answer any travel related queries!")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:  # iterate through all messages
        with st.chat_message(
                message["role"]
        ):  # display below in an expander relative to the role
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask me a travel query!"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        context = """
        You are a travel guide. You will provide the user with the best travel destination based on their preferences in which you will ask the following questions:

        1. What is your MBTI?
        2. What is your age?
        3. What is the duration of the trip?
        4. What is your hobby?

    Using the answers to the questions give an itenarary which is built around the answers given by the user. Make sure the output gives the following:

        1. Country of destination based on the mbti, age and hobby
        2. Specific tourist location and not just a city name but shop/attraction names and a brief description. make sure to suggest enough locations based on the duration given.
        3. A route in which the user can travel to said destinations
        4. Reason of suggesting the destinations based on the mbti, hobby and age of the user.

    You will always start by stating the following:
    "Hi there I am your personal travel guide. I will help you find the best travel destination for you. Please answer the following questions:"
    then ask the user the questions.
        """

        system_message = {"role": "system", "content": f'{context}'}

        st.session_state.messages.append(system_message)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{
                    "role": m["role"],
                    "content": m["content"]
                } for m in st.session_state.messages],
                stream=True,
                max_tokens=500,
                temperature=1.2)
            response = st.write_stream(stream)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

## LIMJUNYI
# Image translation content
with tab2:
    # Streamlit component for image upload
    uploaded_image = st.file_uploader(
        "Upload an image to translate the contents as you need",
        type=["jpg", "png", "jpeg"])

    # Streamlit component for language selection
    languages = {
        "English": "en",
        "Mandarin Chinese": "zh-CN",
        "Hindi": "hi",
        "Spanish": "es",
        "French": "fr",
        "Arabic": "ar",
        "Bengali": "bn",
        "Russian": "ru",
        "Portuguese": "pt",
        "Urdu": "ur"
    }
    target_language = languages[st.selectbox("Translate to?",
                                             list(languages.keys()))]

    if uploaded_image is not None and target_language is not None:
        # Display the original image
        st.image(uploaded_image, caption='Original Image')

        # Save the uploaded image to a temporary file
        with open("temp_image.jpg", "wb") as f:
            f.write(uploaded_image.getbuffer())

        # Extract text from the image
        extracted_text = extract_text_from_image("temp_image.jpg")

        # Translate the extracted text
        translated_text = translate_text(extracted_text, target_language)

        # Display the translated text
        st.write(f"Translated text ({target_language}): {translated_text}")

        # Delete the temporary image file after translation
        os.remove("temp_image.jpg")

with tab3:
    travel_packages_tab()
