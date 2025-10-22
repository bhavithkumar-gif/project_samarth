# analytics.py 
import pandas as pd
from scipy.stats import pearsonr
from rapidfuzz import process

def district_crop_extremes(crop_df, state_x, state_y, crop_name, recent_year=None):
    """
    Returns:
    - district with highest production of crop_name in state_x
    - district with lowest production of crop_name in state_y
    """
    df_x = crop_df[(crop_df['state']==state_x) & (crop_df['crop_name'].str.contains(crop_name, case=False))]
    df_y = crop_df[(crop_df['state']==state_y) & (crop_df['crop_name'].str.contains(crop_name, case=False))]
    
    if recent_year:
        df_x = df_x[df_x['year']==recent_year]
        df_y = df_y[df_y['year']==recent_year]
    else:
        # pick most recent year automatically
        df_x = df_x[df_x['year']==df_x['year'].max()]
        df_y = df_y[df_y['year']==df_y['year'].max()]

    if df_x.empty or df_y.empty:
        return None, None

    max_x = df_x.loc[df_x['production_tonnes'].idxmax()]
    min_y = df_y.loc[df_y['production_tonnes'].idxmin()]

    return {
        "state_x_district_max": max_x['district'],
        "state_x_production": max_x['production_tonnes'],
        "state_x_year": max_x['year']
    }, {
        "state_y_district_min": min_y['district'],
        "state_y_production": min_y['production_tonnes'],
        "state_y_year": min_y['year']
    }

# --- New function: correlate crop production trend with rainfall trend ---
def correlate_crop_climate_trend(crop_df, rain_df, crop_name, region_states, last_n_years=5):
    """
    Returns correlation results for aggregated crop production vs rainfall
    region_states: list of state names
    """
    crop_ts = crop_df[crop_df['state'].isin(region_states) & crop_df['crop_name'].str.contains(crop_name, case=False)]
    crop_agg = crop_ts.groupby('year')['production_tonnes'].sum().sort_index()
    
    rain_ts = rain_df[rain_df['state'].isin(region_states)]
    rain_agg = rain_ts.groupby('year')['rainfall_mm'].sum().sort_index()

    if last_n_years:
        recent_years = sorted(crop_agg.index)[-last_n_years:]
        crop_agg = crop_agg.loc[recent_years]
        rain_agg = rain_agg.loc[recent_years]

    common_years = crop_agg.index.intersection(rain_agg.index)
    if len(common_years) < 3:
        return None
    r, p = pearsonr(crop_agg.loc[common_years], rain_agg.loc[common_years])
    return {"pearson_r": float(r), "p_value": float(p), "years": list(common_years)}
