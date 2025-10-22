import streamlit as st
from analytics import (
    load_crop_df,
    load_rain_df,
    avg_annual_rainfall_for_state,
    top_m_crops_in_state,
    district_crop_extremes,
    correlate_crop_climate_trend,
)

# Must be first Streamlit command
st.set_page_config(page_title="Project Samarth", page_icon="🌾", layout="wide")

st.title("🌾 Project Samarth – Intelligent Q&A System")
st.caption("Analyzing India's Agricultural Economy vs Climate Patterns")

# ------------------ Load Data ------------------
crop_df = load_crop_df()
rain_df = load_rain_df()

if crop_df.empty or rain_df.empty:
    st.error("❌ Data failed to load. Please ensure CSV files are in the same directory.")
    st.stop()

st.sidebar.header("Choose Parameters")

states = sorted(crop_df["state"].unique())
state_x = st.sidebar.selectbox("Select State X", states)
state_y = st.sidebar.selectbox("Select State Y", states)
n_years = st.sidebar.slider("Years to Compare", 1, 5, 3)
m_crops = st.sidebar.slider("Top Crops (M)", 1, 5, 3)

# ------------------ Query 1 ------------------
st.subheader("1️⃣ Compare Average Annual Rainfall and Top Crops")

avg_x, years_x = avg_annual_rainfall_for_state(rain_df, state_x, n_years)
avg_y, years_y = avg_annual_rainfall_for_state(rain_df, state_y, n_years)

if avg_x and avg_y:
    st.write(f"**{state_x}:** {avg_x:.2f} mm (Years: {years_x})")
    st.write(f"**{state_y}:** {avg_y:.2f} mm (Years: {years_y})")

st.write("**Top Crops in Each State:**")
st.write(state_x, top_m_crops_in_state(crop_df, state_x, m_crops))
st.write(state_y, top_m_crops_in_state(crop_df, state_y, m_crops))

# ------------------ Query 2 ------------------
st.subheader("2️⃣ Districts with Max/Min Production for a Crop")

crop_name = st.selectbox("Select Crop to Analyze", sorted(crop_df["crop"].unique()))
state_sel = st.selectbox("Select State", states)
max_row, min_row = district_crop_extremes(crop_df, state_sel, crop_name)
if max_row is not None:
    st.write(
        f"**{state_sel}** ({max_row['year']}): Max Production in **{max_row['district']}** = {max_row['production_tons']} tons"
    )
    st.write(
        f"**{state_sel}** ({min_row['year']}): Min Production in **{min_row['district']}** = {min_row['production_tons']} tons"
    )

# ------------------ Query 3 ------------------
st.subheader("3️⃣ Crop–Climate Correlation")
region = st.selectbox("Select Region for Correlation", states)
corr = correlate_crop_climate_trend(crop_df, rain_df, region)
st.write(f"Correlation between crop production and rainfall in **{region}**: **{corr:.2f}**")

st.info("All outputs are data-driven. Sources: data.gov.in datasets (MoA & IMD)")
