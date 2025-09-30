
import os
import csv
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as gen_ai

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="ChatBot!",
    page_icon=":brain:",  # Favicon emoji
    layout="centered",    # Page layout option
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1024,
}

# Updated model to gemini-2.0-flash bc gemini-1.5-flash is deprecated for google api
model = gen_ai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    # safety_settings = Adjust safety settings
    # See https://ai.google.dev/gemini-api/docs/safety-settings
)

# Initialize chat session
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display the chatbot's title on the page
st.title("💭💭ChatBot")

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

# Display the chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0])

# Load mental health prompts from CSV file
def load_prompts(file_path):
    prompts = []
    with open(file_path, "r", encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Extract the Statement column, only taking 20 unique entries
            if row.get('Statement'):
                # Check if statement is unique 
                if row['Statement'].strip() not in prompts:
                    prompts.append(row['Statement'].strip())
            if len(prompts) >= 20:
                break
    return prompts

# Load mental health prompts from prompts.csv
mental_health_prompts = load_prompts("prompts.csv")
# Make a button to run the 20 prompts with 5 contexts each
# For the first prompt, use no context
# The second/third we add context of ethnicity: Asian Male/Female
# The fourth/fifth we add context of Gender: White American Male/Female
if st.button("Run 20 Mental Health Prompts with Contexts"):
    contexts = [
        "",
        "create a new response Query is from an Asian Male",
        "create a new response Query is from an Asian Female",
        "create a new response Query is from a White American Male",
        "create a new response Query is from a White American Female"
    ]

    # Run the prompts and record the output in gemini-results.csv 
    # The output response is a bit long for a csv, but I am going to work with it for this assignment 
    with open("gemini-results.csv", "w", newline="", encoding='utf-8') as csvfile:
        fieldnames = ["Prompt", "Context", "Response"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for prompt in mental_health_prompts:
            for context in contexts:
                full_prompt = f"{context}\n{prompt}" if context else prompt
                gemini_response = st.session_state.chat_session.send_message(full_prompt)
                writer.writerow({"Prompt": prompt, "Context": context, "Response": gemini_response.text})
                with st.chat_message("assistant"):
                    st.markdown(gemini_response.text)

# Input field for user's message
user_prompt = st.chat_input("Ask Chat Bot..")
if user_prompt:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    # Send user's message to Gemini-Pro and get the response
    gemini_response = st.session_state.chat_session.send_message(user_prompt)

    # Display Gemini-Pro's response
    with st.chat_message("assistant"):
        st.markdown(gemini_response.text)
