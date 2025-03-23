import streamlit as st
import pandas as pd
from openai import OpenAI

# Set page title and description.
st.title("💬 Medical Case Chatbot")
st.write(
    "This chatbot presents a medical case based on the details you provide and guides a stepwise evaluation. "
    "At the end of the conversation, the AI will summarize your plan. "
    "You also have the option to save the full conversation as a CSV file."
)

# Input for medical case details.
case_details = st.text_area(
    "Enter the details for the ER patient case (e.g., age, symptoms, vitals)",
    placeholder="e.g., 65-year-old, dizziness, slight confusion, blood pressure 140/90..."
)

# Button to start the case-based conversation.
if st.button("Start Medical Case Chat"):
    if case_details:
        # Initialize session state messages.
        st.session_state.messages = []
        # Create a system prompt that sets the context for the conversation.
        initial_prompt = (
            f"You are a medical educator. Present a medical case of an ER patient with dizziness. "
            f"Here are the patient details: {case_details}. "
            "Your task is to prompt the user for a stepwise evaluation of the patient, ask clarifying questions, "
            "and at the end, summarize the user’s plan. "
            "Ensure the conversation stays focused on the clinical evaluation."
        )
        st.session_state.messages.append({"role": "system", "content": initial_prompt})
        st.success("Medical Case Chat started!")
    else:
        st.error("Please provide case details to start the conversation.")

# Ask for the OpenAI API key.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Ensure messages exist in session state.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing chat messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for the user.
    if prompt := st.chat_input("Your response..."):
        # Store the user’s prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response from the AI using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Add a save button to download the conversation as CSV.
    if st.button("Save Conversation"):
        if st.session_state.messages:
            # Convert messages to a DataFrame.
            df = pd.DataFrame(st.session_state.messages)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Conversation as CSV",
                data=csv,
                file_name="conversation.csv",
                mime="text/csv"
            )
        else:
            st.warning("No conversation to save yet!")
