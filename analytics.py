import pandas as pd
import matplotlib.pyplot as plt
import io

def load_crop_df(path="crop_production.csv"):
    return pd.read_csv(path)

def load_rain_df(path="rainfall.csv"):
    return pd.read_csv(path)

def answer_question(crop_df, rain_df, question):
    q = question.lower()
    img = None   # chart placeholder
    answer = ""

    # 🌾 1. Highest crop production
    if "highest" in q:
        for crop in crop_df["Crop"].str.lower().unique():
            if crop in q:
                year = None
                for y in crop_df["Year"].unique():
                    if str(y) in q:
                        year = y
                        break
                df = crop_df[crop_df["Crop"].str.lower() == crop]
                if year:
                    df = df[df["Year"] == year]
                grouped = df.groupby("State")["production_tons"].sum()
                top_state = grouped.idxmax()
                top_val = grouped.max()
                answer = f"{top_state} had the highest {crop.title()} production ({top_val} tons) in {year if year else 'all years combined'}."
                break

    # 🌦️ 2. Rainfall analysis
    elif "rainfall" in q:
        for state in rain_df["State"].unique():
            if state.lower() in q:
                sub = rain_df[rain_df["State"] == state]
                avg = round(sub["Rainfall_mm"].mean(), 1)
                answer = f"The average rainfall in {state} was {avg} mm from {sub['Year'].min()} to {sub['Year'].max()}."
                if any(word in q for word in ["trend", "graph", "chart", "show"]):
                    plt.figure(figsize=(6, 4))
                    plt.plot(sub["Year"], sub["Rainfall_mm"], marker="o")
                    plt.title(f"Rainfall Trend in {state}")
                    plt.xlabel("Year")
                    plt.ylabel("Rainfall (mm)")
                    plt.grid(True)
                    buf = io.BytesIO()
                    plt.savefig(buf, format="png", bbox_inches="tight")
                    buf.seek(0)
                    img = buf
                break

    # 📊 3. Crop trend analysis
    elif any(word in q for word in ["trend", "show", "chart", "graph"]):
        for crop in crop_df["Crop"].str.lower().unique():
            if crop in q:
                for state in crop_df["State"].unique():
                    if state.lower() in q:
                        sub = crop_df[(crop_df["Crop"].str.lower() == crop) & (crop_df["State"] == state)]
                        plt.figure(figsize=(6, 4))
                        plt.plot(sub["Year"], sub["production_tons"], marker="o")
                        plt.title(f"{crop.title()} Production Trend in {state}")
                        plt.xlabel("Year")
                        plt.ylabel("production (tons)")
                        plt.grid(True)
                        buf = io.BytesIO()
                        plt.savefig(buf, format="png", bbox_inches="tight")
                        buf.seek(0)
                        img = buf
                        answer = f"Here’s the {crop.title()} production trend in {state}."
                        return answer, img

    if answer == "":
        answer = "Sorry, I couldn’t interpret that question yet. Try asking about a crop, rainfall, or trend."

    return answer, img
