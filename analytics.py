import pandas as pd

# ------------------ DATA LOADING ------------------
def load_crop_df(path="crop_production_large.csv"):
    try:
        df = pd.read_csv(path)
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except Exception as e:
        print("Error loading crop data:", e)
        return pd.DataFrame()

def load_rain_df(path="rainfall.csv"):
    try:
        df = pd.read_csv(path)
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except Exception as e:
        print("Error loading rainfall data:", e)
        return pd.DataFrame()

# ------------------ ANALYTICAL FUNCTIONS ------------------
def avg_annual_rainfall_for_state(df, state, n_years):
    if df.empty:
        return None, []
    df_state = df[df["state"].str.lower() == state.lower()]
    recent_years = sorted(df_state["year"].unique())[-n_years:]
    avg_rain = df_state[df_state["year"].isin(recent_years)]["rainfall_mm"].mean()
    return avg_rain, recent_years

def top_m_crops_in_state(df, state, m):
    if df.empty:
        return pd.DataFrame()
    df_state = df[df["state"].str.lower() == state.lower()]
    result = (
        df_state.groupby("crop")["production_tons"]
        .sum()
        .nlargest(m)
        .reset_index()
    )
    return result

def district_crop_extremes(df, state, crop):
    if df.empty:
        return None, None
    df_crop = df[
        (df["state"].str.lower() == state.lower())
        & (df["crop"].str.lower() == crop.lower())
    ]
    if df_crop.empty:
        return None, None
    recent_year = df_crop["year"].max()
    df_recent = df_crop[df_crop["year"] == recent_year]
    max_row = df_recent.loc[df_recent["production_tons"].idxmax()]
    min_row = df_recent.loc[df_recent["production_tons"].idxmin()]
    return max_row, min_row

def correlate_crop_climate_trend(crop_df, rain_df, region):
    crop_region = (
        crop_df[crop_df["state"].str.lower() == region.lower()]
        .groupby("year")["production_tons"]
        .sum()
        .reset_index()
    )
    rain_region = (
        rain_df[rain_df["state"].str.lower() == region.lower()]
        .groupby("year")["rainfall_mm"]
        .mean()
        .reset_index()
    )
    merged = pd.merge(crop_region, rain_region, on="year", how="inner")
    correlation = merged["production_tons"].corr(merged["rainfall_mm"])
    return correlation
