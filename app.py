import streamlit as st
from analytics import load_crop_df, load_rain_df, answer_question

st.title("🌾 Crop & Rainfall Q&A System")

# Load data
crop_df = load_crop_df()
rain_df = load_rain_df()

# Input box for question
question = st.text_input("Ask a question (e.g., 'Which state had highest rice production in 2020?')")

if question:
    with st.spinner("Analyzing..."):
        answer = answer_question(crop_df, rain_df, question)
        st.success(answer)
