# analytics.py
import pandas as pd
from scipy.stats import pearsonr

def load_crop_df(path):
    import pandas as pd
    return pd.read_csv(path)

def load_rain_df(path):
    import pandas as pd
    return pd.read_csv(path)
    
def avg_annual_rainfall_for_state(rain_df, state, n_years):
    df = rain_df[rain_df['state'] == state]
    recent_years = sorted(df['year'].unique())[-n_years:]
    return df[df['year'].isin(recent_years)]['rainfall_mm'].mean()

def top_m_crops_in_state(crop_df, state, n_years, m, crop_filter=None):
    df = crop_df[crop_df['state'] == state]
    recent_years = sorted(df['year'].unique())[-n_years:]
    df = df[df['year'].isin(recent_years)]
    if crop_filter:
        df = df[df['crop_name'].str.contains(crop_filter, case=False)]
    top_crops = df.groupby('crop_name')['production_tonnes'].sum().sort_values(ascending=False).head(m)
    return top_crops.reset_index()

def district_crop_extremes(crop_df, state_x, state_y, crop_name):
    df_x = crop_df[(crop_df['state'] == state_x) & (crop_df['crop_name'].str.contains(crop_name, case=False))]
    df_y = crop_df[(crop_df['state'] == state_y) & (crop_df['crop_name'].str.contains(crop_name, case=False))]
    df_x = df_x[df_x['year'] == df_x['year'].max()]
    df_y = df_y[df_y['year'] == df_y['year'].max()]
    if df_x.empty or df_y.empty:
        return None, None
    max_x = df_x.loc[df_x['production_tonnes'].idxmax()]
    min_y = df_y.loc[df_y['production_tonnes'].idxmin()]
    return {
        "district_max": max_x['district'],
        "production": max_x['production_tonnes'],
        "year": max_x['year']
    }, {
        "district_min": min_y['district'],
        "production": min_y['production_tonnes'],
        "year": min_y['year']
    }

def correlate_crop_climate_trend(crop_df, rain_df, crop_name, states, last_n_years=5):
    crop_ts = crop_df[crop_df['state'].isin(states) & crop_df['crop_name'].str.contains(crop_name, case=False)]
    crop_agg = crop_ts.groupby('year')['production_tonnes'].sum().sort_index()
    rain_ts = rain_df[rain_df['state'].isin(states)]
    rain_agg = rain_ts.groupby('year')['rainfall_mm'].sum().sort_index()
    recent_years = sorted(crop_agg.index)[-last_n_years:]
    crop_agg = crop_agg.loc[recent_years]
    rain_agg = rain_agg.loc[recent_years]
    common_years = crop_agg.index.intersection(rain_agg.index)
    if len(common_years) < 3:
        return None
    r, p = pearsonr(crop_agg.loc[common_years], rain_agg.loc[common_years])
    return {"pearson_r": float(r), "p_value": float(p), "years": list(common_years)}
