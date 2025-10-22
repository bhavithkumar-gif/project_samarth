# app.py
import streamlit as st
from analytics import load_crop_df, load_rain_df, avg_annual_rainfall_for_state, top_m_crops_in_state
import os

st.set_page_config(page_title="Project Samarth — Prototype Q&A", layout="centered")
st.title("Project Samarth — Agriculture + Climate Q&A (Prototype)")

st.markdown("""
**Demo intent implemented:**  
**Compare average annual rainfall in State A and State B for the last N years** and **list top M crops (by production)** in each state across the same period.  
Sources: district crop production CSV (data/...) and IMD rainfall CSV (data/...).  
(If `data/` is empty, the app will attempt to use `sample_outputs/`.)
""")

# Load datasets (simple: picks first CSV in data/ or sample_outputs/)
def find_csv(folder):
    if not os.path.exists(folder): return None
    for f in os.listdir(folder):
        if f.lower().endswith('.csv'):
            return os.path.join(folder, f)
    return None

crop_path = find_csv('data') or find_csv('sample_outputs')
rain_path = find_csv('data') or find_csv('sample_outputs')

st.sidebar.header("Demo inputs")
state_x = st.sidebar.text_input("State X (e.g., Maharashtra)", "Maharashtra")
state_y = st.sidebar.text_input("State Y (e.g., Karnataka)", "Karnataka")
N = st.sidebar.number_input("Last N years (use small number for demo)", min_value=1, max_value=50, value=5)
M = st.sidebar.number_input("Top M crops", min_value=1, max_value=10, value=3)
crop_filter = st.sidebar.text_input("Crop type filter (optional, e.g., Rice)", "")

st.write("**Data files used (if present)**")
st.write("Crop CSV used:", crop_path or "None (use sample_outputs/)")
st.write("Rain CSV used:", rain_path or "None (use sample_outputs/)")

if st.button("Run: Compare rainfall + top crops"):
    if not (crop_path and rain_path):
        st.error("No CSVs found. Please run discover_and_download.py OR use sample CSVs in sample_outputs/.")
    else:
        try:
            crop_df = load_crop_df(crop_path)
            rain_df = load_rain_df(rain_path)
        except Exception as e:
            st.error("Error loading datasets: " + str(e))
            st.stop()

        avg_x, yearly_x = avg_annual_rainfall_for_state(rain_df, state_x, N)
        avg_y, yearly_y = avg_annual_rainfall_for_state(rain_df, state_y, N)
        topx, years_x = top_m_crops_in_state(crop_df, state_x, N, M, crop_filter or None)
        topy, years_y = top_m_crops_in_state(crop_df, state_y, N, M, crop_filter or None)

        st.subheader("Rainfall comparison (average annual)")
        if avg_x is None:
            st.write(f"No rainfall data found for {state_x} in provided dataset.")
        else:
            st.write(f"{state_x} — **{avg_x:.1f} mm** (avg annual over years: {list(yearly_x['year'].values)})")
            st.caption(f"Derived from: {os.path.basename(rain_path)}")

        if avg_y is None:
            st.write(f"No rainfall data found for {state_y} in provided dataset.")
        else:
            st.write(f"{state_y} — **{avg_y:.1f} mm** (avg annual over years: {list(yearly_y['year'].values)})")
            st.caption(f"Derived from: {os.path.basename(rain_path)}")

        st.subheader("Top crops by production (aggregated over selected years)")
        if topx is None or topx.empty:
            st.write(f"No crop production data for {state_x}")
        else:
            st.write(f"Top {M} crops in {state_x} (aggregated over {years_x}):")
            st.dataframe(topx.reset_index(drop=True))
            st.caption(f"Derived from: {os.path.basename(crop_path)}")

        if topy is None or topy.empty:
            st.write(f"No crop production data for {state_y}")
        else:
            st.write(f"Top {M} crops in {state_y} (aggregated over {years_y}):")
            st.dataframe(topy.reset_index(drop=True))
            st.caption(f"Derived from: {os.path.basename(crop_path)}")

        # Offer CSV download of the used rows
        st.markdown("---")
        st.write("Download exact rows used for audit:")
        rows_used = pd.concat([
            crop_df[(crop_df['state']==state_x)&(crop_df['year'].isin(years_x or []))],
            crop_df[(crop_df['state']==state_y)&(crop_df['year'].isin(years_y or []))]
        ], ignore_index=True)
        st.download_button("Download crop rows used (CSV)", rows_used.to_csv(index=False).encode('utf-8'), file_name='rows_used_crops.csv')
