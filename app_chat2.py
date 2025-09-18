import streamlit as st
import pandas as pd

# ===============================
# Initialize session state
# ===============================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.user_data = {}
    st.session_state.filtered = pd.DataFrame()
    st.session_state.index = 0

# ===============================
# Load data from Google Sheets
# ===============================
sheet_url = "https://docs.google.com/spreadsheets/d/1kFlaF27Ff1XwfFNaqO4EJ5XzlZkwCmcA0ggnO3fSW_4/export?format=csv"
df = pd.read_csv(sheet_url)

# ===============================
# Helper function
# ===============================
def filter_internships(major, grad_year, industry, location):
    filtered = df[
        df["Eligible Majors"].str.contains(major, case=False) &
        (df["Graduation Year Min"] <= grad_year) &
        (df["Graduation Year Max"] >= grad_year) &
        df["Industry"].str.contains(industry, case=False)
    ]
    if location:
        filtered = filtered[filtered["Location"].str.contains(location, case=False)]
    return filtered.reset_index(drop=True)

# ===============================
# Display past messages
# ===============================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ===============================
# Chat input
# ===============================
if prompt := st.chat_input("Type your response..."):

    # Record user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Conversation flow
    if st.session_state.step == 0:
        st.session_state.user_data["major"] = prompt
        response = "Great! What year are you graduating?"
        st.session_state.step = 1

    elif st.session_state.step == 1:
        st.session_state.user_data["grad_year"] = int(prompt)
        response = "Nice. Which industry are you interested in?"
        st.session_state.step = 2

    elif st.session_state.step == 2:
        st.session_state.user_data["industry"] = prompt
        response = "Got it. Do you have a preferred location? (Optional, type 'skip')"
        st.session_state.step = 3

    elif st.session_state.step == 3:
        st.session_state.user_data["location"] = "" if prompt.lower() == "skip" else prompt
        st.session_state.filtered = filter_internships(
            st.session_state.user_data["major"],
            st.session_state.user_data["grad_year"],
            st.session_state.user_data["industry"],
            st.session_state.user_data["location"]
        )
        st.session_state.index = 0
        if len(st.session_state.filtered) > 0:
            batch = st.session_state.filtered.iloc[0:5]
            response = "Here are 5 internships I found for you:\n"
            for _, row in batch.iterrows():
                response += f"- **{row['Internship Title']}** at {row['Company']} ([Link]({row['Link']}))\n"
            response += "\nDo you want to see more?"
            st.session_state.index = 5
            st.session_state.step = 4
        else:
            response = "Sorry, I couldn't find any internships. Do you want to try another industry or location?"

    elif st.session_state.step == 4:
        if prompt.lower() in ["yes", "y", "more"]:
            start, end = st.session_state.index, st.session_state.index + 5
            batch = st.session_state.filtered.iloc[start:end]
            if not batch.empty:
                response = "Here are more internships:\n"
                for _, row in batch.iterrows():
                    response += f"- **{row['Internship Title']}** at {row['Company']} ([Link]({row['Link']}))\n"
                response += "\nDo you want to see more?"
                st.session_state.index += 5
            else:
                response = "Oops, we’ve reached the end of the list. Do you want to look into another industry or location?"
        else:
            response = "Okay! Do you want to search by another industry or location?"

    # Record assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
