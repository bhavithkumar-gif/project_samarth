import pandas as pd

def load_crop_df(path="crop_production_large.csv"):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns] 
    return df
    except Exception as e:
        print(f"Error loading crop CSV: {e}")
        return pd.DataFrame()

def load_rain_df(path="rainfall_large.csv"):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]  
    return df

    except Exception as e:
        print(f"Error loading rain CSV: {e}")
        return pd.DataFrame()

def avg_annual_rainfall_for_state(df, state, N):
    state_df = df[df['state'] == state]
    recent_years = sorted(state_df['year'].unique())[-N:]
    avg_rainfall = state_df[state_df['year'].isin(recent_years)]['rainfall_mm'].mean()
    return avg_rainfall, recent_years

def top_m_crops_in_state(df, state, N, M):
    recent_years = sorted(df['year'].unique())[-N:]
    filtered = df[(df['state'] == state) & (df['year'].isin(recent_years))]
    top_crops = (filtered.groupby('crop_name')['production_tonnes']
                 .sum().sort_values(ascending=False).head(M))
    return top_crops
