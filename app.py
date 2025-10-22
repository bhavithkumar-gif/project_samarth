import streamlit as st
import os
from analytics import load_crop_df, load_rain_df, avg_annual_rainfall_for_state, top_m_crops_in_state

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
crop_path = os.path.join(BASE_DIR, "sample_outputs/crop_sample.csv")
rain_path = os.path.join(BASE_DIR, "sample_outputs/rain_sample.csv")

# Load data
crop_df = load_crop_df(crop_path)
rain_df = load_rain_df(rain_path)

st.set_page_config(page_title="Project Samarth", page_icon="🌾", layout="wide")

st.title("🌾 Project Samarth: Agricultural & Climate Insights")
st.markdown("""
Compare **average rainfall** and **top crops** across states for the last N years, 
using real data from Government of India repositories (sample version).
""")

st.sidebar.header("🔧 Input Parameters")
state_x = st.sidebar.selectbox("Select State X", sorted(crop_df['state'].unique()))
state_y = st.sidebar.selectbox("Select State Y", sorted(crop_df['state'].unique()))
N = st.sidebar.slider("Select number of recent years (N)", 1, 5, 3)
M = st.sidebar.slider("Select top M crops", 1, 5, 3)

if st.sidebar.button("Analyze"):
    try:
        # Average Rainfall
        avg_x, years_x = avg_annual_rainfall_for_state(rain_df, state_x, N)
        avg_y, years_y = avg_annual_rainfall_for_state(rain_df, state_y, N)
        st.subheader("🌦️ Average Annual Rainfall Comparison")
        st.write(f"{state_x}: **{avg_x:.2f} mm** (Years: {years_x})")
        st.write(f"{state_y}: **{avg_y:.2f} mm** (Years: {years_y})")

        # Top crops
        top_x = top_m_crops_in_state(crop_df, state_x, N, M)
        top_y = top_m_crops_in_state(crop_df, state_y, N, M)
        st.subheader("🌾 Top Crops by Production (Last N Years)")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{state_x}**")
            st.dataframe(top_x)
        with col2:
            st.write(f"**{state_y}**")
            st.dataframe(top_y)

        st.info(f"Data Sources: {os.path.basename(crop_path)}, {os.path.basename(rain_path)}")

    except Exception as e:
        st.error(f"Error: {e}")
