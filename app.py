# app.py
import streamlit as st
from analytics import load_crop_df, load_rain_df, avg_annual_rainfall_for_state, top_m_crops_in_state, district_crop_extremes, correlate_crop_climate_trend
import os
import pandas as pd

st.set_page_config(page_title="Project Samarth — Prototype Q&A", layout="wide")
st.title("Project Samarth — Agriculture + Climate Q&A Prototype")

# Load datasets
def find_csv(folder):
    if not os.path.exists(folder): return None
    for f in os.listdir(folder):
        if f.lower().endswith('.csv'):
            return os.path.join(folder, f)
    return None

crop_path = find_csv('data') or find_csv('sample_outputs')
rain_path = find_csv('data') or find_csv('sample_outputs')

try:
    crop_df = load_crop_df(crop_path)
    rain_df = load_rain_df(rain_path)
except Exception as e:
    st.error(f"Error loading CSVs: {e}")
    st.stop()

tabs = st.tabs(["Rainfall + Top Crops", "District Crop Comparison", "Crop-Climate Correlation"])

# --- Tab 1: Rainfall + Top Crops (existing demo) ---
with tabs[0]:
    st.subheader("Compare average rainfall and top crops")
    state_x = st.text_input("State X", "Maharashtra", key="tab0x")
    state_y = st.text_input("State Y", "Karnataka", key="tab0y")
    N = st.number_input("Last N years", min_value=1, max_value=50, value=5, key="tab0n")
    M = st.number_input("Top M crops", min_value=1, max_value=10, value=3, key="tab0m")
    crop_filter = st.text_input("Crop filter (optional)", "", key="tab0crop")
    if st.button("Run", key="tab0btn"):
        avg_x, _ = avg_annual_rainfall_for_state(rain_df, state_x, N)
        avg_y, _ = avg_annual_rainfall_for_state(rain_df, state_y, N)
        topx, _ = top_m_crops_in_state(crop_df, state_x, N, M, crop_filter or None)
        topy, _ = top_m_crops_in_state(crop_df, state_y, N, M, crop_filter or None)
        st.write(f"{state_x} avg rainfall: {avg_x:.1f} mm, {state_y} avg rainfall: {avg_y:.1f} mm")
        st.write(f"Top {M} crops in {state_x}")
        st.dataframe(topx)
        st.write(f"Top {M} crops in {state_y}")
        st.dataframe(topy)

# --- Tab 2: District-level crop comparison ---
with tabs[1]:
    st.subheader("District-level crop extremes")
    state_x2 = st.text_input("State X", "Maharashtra", key="tab1x")
    state_y2 = st.text_input("State Y", "Karnataka", key="tab1y")
    crop_name2 = st.text_input("Crop name (e.g., Rice)", "Rice", key="tab1crop")
    if st.button("Run district comparison", key="tab1btn"):
        max_x, min_y = district_crop_extremes(crop_df, state_x2, state_y2, crop_name2)
        if max_x and min_y:
            st.write(f"{state_x2} district with max {crop_name2}: {max_x['state_x_district_max']} ({max_x['state_x_production']} t in {max_x['state_x_year']})")
            st.write(f"{state_y2} district with min {crop_name2}: {min_y['state_y_district_min']} ({min_y['state_y_production']} t in {min_y['state_y_year']})")
        else:
            st.write("Data not sufficient for district comparison.")

# --- Tab 3: Crop-climate correlation ---
with tabs[2]:
    st.subheader("Crop-climate correlation")
    crop_name3 = st.text_input("Crop name (e.g., Rice)", "Rice", key="tab2crop")
    states3 = st.text_input("States (comma-separated)", "Maharashtra,Karnataka", key="tab2states")
    last_n3 = st.number_input("Last N years", min_value=1, max_value=50, value=5, key="tab2n")
    if st.button("Run correlation", key="tab2btn"):
        state_list = [s.strip() for s in states3.split(',')]
        result = correlate_crop_climate_trend(crop_df, rain_df, crop_name3, state_list, last_n3)
        if result:
            st.write(f"Pearson correlation r={result['pearson_r']:.2f}, p-value={result['p_value']:.4f}, years={result['years']}")
        else:
            st.write("Not enough data to compute correlation.")
