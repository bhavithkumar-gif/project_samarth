import streamlit as st
from analytics import load_crop_df, load_rain_df, answer_question
from PIL import Image

st.set_page_config(page_title="Smart Crop & Rainfall Q&A", page_icon="🌾", layout="centered")
st.title("🌾 Smart Crop & Rainfall Q&A System")

st.write("Ask me questions like:")
st.markdown("""
- **Which state had highest rice production in 2020?**  
- **Show rainfall trend for Karnataka**  
- **Display wheat production graph in Punjab**  
""")

crop_df = load_crop_df()
rain_df = load_rain_df()

question = st.text_input("🧠 Type your question:")

if question:
    with st.spinner("Analyzing..."):
        answer, img = answer_question(crop_df, rain_df, question)
        st.success(answer)
        if img:
            image = Image.open(img)
            st.image(image, caption="Generated Chart")
