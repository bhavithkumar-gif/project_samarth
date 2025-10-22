# analytics.py
import pandas as pd
from scipy.stats import pearsonr
from datetime import datetime
from rapidfuzz import process, fuzz

def load_crop_df(path):
    # tries common column names; returns normalized columns: ['state','district','year','crop_name','production_tonnes']
    df = pd.read_csv(path, low_memory=False)
    cols = {c.lower():c for c in df.columns}
    # heuristics:
    mapping = {}
    if 'state' in cols: mapping['state']=cols['state']
    elif 'state_name' in cols: mapping['state']=cols['state_name']
    if 'district' in cols: mapping['district']=cols['district']
    if 'year' in cols: mapping['year']=cols['year']
    for k in ['crop','crop_name','crop_name_english']:
        if k in cols and 'crop_name' not in mapping:
            mapping['crop_name']=cols[k]
    for k in ['production','production_tonnes','production (tonnes)']:
        if k in cols and 'production_tonnes' not in mapping:
            mapping['production_tonnes']=cols[k]
    df = df.rename(columns={v:k for k,v in mapping.items()})
    # enforce columns
    for req in ['state','year','crop_name','production_tonnes']:
        if req not in df.columns:
            raise ValueError(f"Required column '{req}' not found in crop CSV.")
    df['year'] = df['year'].astype(int)
    df['production_tonnes'] = pd.to_numeric(df['production_tonnes'], errors='coerce').fillna(0)
    df['state'] = df['state'].str.strip()
    df['crop_name'] = df['crop_name'].astype(str).str.strip()
    return df[['state','district','year','crop_name','production_tonnes']]

def load_rain_df(path):
    # expects columns: state, year, month(optional), rainfall_mm or monthly_mm
    df = pd.read_csv(path, low_memory=False)
    cols = {c.lower():c for c in df.columns}
    if 'state' not in cols:
        raise ValueError("No state column in rainfall CSV.")
    # try to find rainfall column
    rf_col = None
    for candidate in ['rainfall_mm','rainfall','monthly_rainfall','mm']:
        if candidate in cols:
            rf_col = cols[candidate]; break
    if rf_col is None:
        # try to find any numeric column aside from year
        for c in df.columns:
            if c.lower() not in ('state','year','month') and pd.api.types.is_numeric_dtype(df[c]):
                rf_col = c; break
    df = df.rename(columns={cols['state']:'state', cols.get('year','year'):'year'})
    if 'year' not in df.columns:
        # try parse from date columns
        for c in df.columns:
            if 'date' in c.lower():
                df['year'] = pd.to_datetime(df[c]).dt.year
                break
    if rf_col:
        df['rainfall_mm'] = pd.to_numeric(df[rf_col], errors='coerce').fillna(0)
    else:
        raise ValueError("Could not locate rainfall numeric column.")
    df['year'] = df['year'].astype(int)
    df['state'] = df['state'].str.strip()
    return df[['state','year','rainfall_mm']]

def avg_annual_rainfall_for_state(rain_df, state_name, last_n_years):
    years = sorted(rain_df[rain_df['state']==state_name]['year'].unique(), reverse=True)[:last_n_years]
    if not years:
        return None, []
    sel = rain_df[(rain_df['state']==state_name)&(rain_df['year'].isin(years))]
    yearly = sel.groupby('year')['rainfall_mm'].sum().reset_index().sort_values('year')
    avg = yearly['rainfall_mm'].mean()
    return float(avg), yearly

def top_m_crops_in_state(crop_df, state_name, last_n_years, M=3, crop_type_filter=None):
    years = sorted(crop_df[crop_df['state']==state_name]['year'].unique(), reverse=True)[:last_n_years]
    sel = crop_df[(crop_df['state']==state_name)&(crop_df['year'].isin(years))]
    if crop_type_filter:
        sel = sel[sel['crop_name'].str.contains(crop_type_filter, case=False, na=False)]
    agg = sel.groupby('crop_name')['production_tonnes'].sum().reset_index().sort_values('production_tonnes', ascending=False)
    return agg.head(M), years

def correlate_crop_with_rain(crop_ts, rain_ts):
    # crop_ts & rain_ts: pandas.Series indexed by year
    common = sorted(set(crop_ts.index).intersection(rain_ts.index))
    if len(common) < 3:
        return None  # insufficient data
    x = crop_ts.loc[common].values
    y = rain_ts.loc[common].values
    r, p = pearsonr(x, y)
    return {"pearson_r": float(r), "p_value": float(p), "years": common}
