import pandas as pd

def load_crop_df(path="crop_production_medium.csv"):
    return pd.read_csv(path)

def load_rain_df(path="rainfall_medium.csv"):
    return pd.read_csv(path)

def answer_question(crop_df, rain_df, question):
    q = question.lower()

    # Example 1: Which state had highest rice production in 2020?
    if "highest" in q and "rice" in q:
        year = 2020 if "2020" in q else None
        df = crop_df[crop_df["Crop"].str.lower() == "rice"]
        if year:
            df = df[df["Year"] == year]
        top = df.groupby("State")["Production_Tons"].sum().idxmax()
        val = df.groupby("State")["Production_Tons"].sum().max()
        return f"{top} had the highest rice production ({val} tons) in {year if year else 'the given years'}."

    # Example 2: rainfall trend for a state
    elif "rainfall" in q:
        for state in rain_df["State"].unique():
            if state.lower() in q:
                sub = rain_df[rain_df["State"] == state]
                avg = round(sub["Rainfall_mm"].mean(), 1)
                return f"The average rainfall in {state} was {avg} mm between {sub['Year'].min()} and {sub['Year'].max()}."
    
    return "Sorry, I couldn't understand that question yet."
