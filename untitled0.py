
import pandas as pd
import spacy
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px
import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import os

random.seed(42)

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.error("spaCy model not found. Run: python -m spacy download en_core_web_sm")
    exit(1)

# --- Phase 1: Prototype ---
# Mock news dataset
flu_articles = [
    "Bird Flu Hits Banjara Hills: 1,000 Birds Culled - Poultry farms scramble.",
    "Gachibowli Flu Surge: Fever Cases Up 20% - Hospitals busy.",
    "Madhapur Flu Fears: Chicken Sales Drop - Panic spreads.",
    "Kukatpally Flu Season Peaks: Coughs Everywhere - Clinics packed.",
    "Secunderabad Bird Flu: 3,000 Chickens Dead - Alert issued.",
    "Hitech City Flu Spike: 50 Cases Today - Health dept steps in."
]
noise_articles = [
    "Banjara Hills Traffic Chaos: No Flu, Just Jams - Roads clogged.",
    "Gachibowli Rain Woes: Sick of Floods - Weather sucks.",
    "Madhapur Heatwave: No Outbreak - Summer hits hard."
]
locations = ["Banjara Hills", "Gachibowli", "Madhapur", "Kukatpally", "Secunderabad", "Hitech City"]

# Generate 200 articles (last 14 days for broader range)
articles = []
base_date = datetime.now() - timedelta(days=14)  # Start 14 days ago
for i in range(200):
    loc = random.choice(locations)
    if random.random() < 0.7:
        text = random.choice(flu_articles).replace("Hyderabad", loc)
    else:
        text = random.choice(noise_articles).replace("Hyderabad", loc)
    date = (base_date + timedelta(days=i//20)).strftime("%Y-%m-%d")
    articles.append({"Text": text, "Location": loc, "Date": date})

news_df = pd.DataFrame(articles)

# Mock flu cases (last 14 days)
dates = [(datetime.now() - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(14, -1, -1)]  # Last 15 days
mock_cases = []
for date in dates:
    for loc in locations:
        mock_cases.append({
            "Date": date,
            "Cases": random.randint(0, 10),
            "Location": loc
        })
cases_df = pd.DataFrame(mock_cases)

# Mock weather data (last 14 days)
mock_weather = {
    "Date": dates,
    "Temperature": [28, 30, 25, 22, 26, 29, 27, 28, 30, 24, 23, 26, 29, 27, 28],
    "Humidity": [40, 35, 50, 60, 45, 40, 55, 50, 38, 52, 58, 47, 42, 53, 49],
    "Rainfall": [0, 0, 5, 10, 0, 0, 2, 0, 1, 3, 8, 0, 0, 4, 0]
}
weather_df = pd.DataFrame(mock_weather)

news_df.to_csv("mock_news.csv", index=False)
cases_df.to_csv("mock_cases.csv", index=False)
weather_df.to_csv("mock_weather.csv", index=False)

def count_flu_mentions(text):
    doc = nlp(text.lower())
    flu_keywords = ["flu", "fever", "cough", "bird flu"]
    return sum(1 for token in doc if token.text in flu_keywords)

news_df["Flu_Mentions"] = news_df["Text"].apply(count_flu_mentions)

all_dates = pd.date_range(start=base_date, end=datetime.now(), freq="D").strftime("%Y-%m-%d").tolist()
all_combinations = pd.DataFrame(
    [(d, loc) for d in all_dates for loc in locations],
    columns=["Date", "Location"]
)

daily_summary = news_df.groupby(["Date", "Location"])["Flu_Mentions"].sum().reset_index()
daily_summary = all_combinations.merge(daily_summary, on=["Date", "Location"], how="left").fillna({"Flu_Mentions": 0})

daily_summary = daily_summary.merge(cases_df, on=["Date", "Location"], how="left").fillna({"Cases": 0})
daily_summary = daily_summary.merge(weather_df, on="Date", how="left").fillna({"Temperature": 25, "Humidity": 40, "Rainfall": 0})

# Basic risk prediction
daily_summary["Base_Risk"] = daily_summary["Flu_Mentions"] * 5 + daily_summary["Cases"] * 2

# --- Phase 2: Core Features ---
# Weather-adjusted risk
def adjust_risk(row):
    risk = row["Base_Risk"]
    if row["Temperature"] < 25:
        risk += 10
    if row["Humidity"] > 50:
        risk += 5
    if row["Rainfall"] > 0:
        risk += 5
    return risk

daily_summary["Total_Risk"] = daily_summary.apply(adjust_risk, axis=1)

# Crowdsourcing
if not os.path.exists("user_reports.csv"):
    mock_reports = {
        "Symptom": ["fever", "cough", "flu", "fever", "cough"],
        "Location": ["Gachibowli", "Madhapur", "Kukatpally", "Hitech City", "Banjara Hills"],
        "Date": [dates[-5], dates[-4], dates[-3], dates[-2], dates[-1]]
    }
    pd.DataFrame(mock_reports).to_csv("user_reports.csv", index=False)

# --- Streamlit App ---
# CSS for compact layout
st.markdown(
    """
    <style>
    .main > div {
        max-width: 800px;
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("AI Public Health Tracker")
st.write("Tracking flu outbreaks in Hyderabad with AI!")

# Crowdsourcing form
st.header("Report Symptoms")
symptom = st.text_input("Enter your symptom (e.g., fever, cough):")
location = st.selectbox("Your location:", locations)
# Flexible date picker (past 1 year to 1 year ahead)
today = datetime.now()
selected_date = st.date_input(
    "Select date:",
    value=today,
    min_value=today - timedelta(days=365),  # 1 year back
    max_value=today + timedelta(days=365)   # 1 year forward
)
if st.button("Submit"):
    if symptom.strip() and location:
        report_date = selected_date.strftime("%Y-%m-%d")
        with open("user_reports.csv", "a") as f:
            f.write(f"{symptom.strip()},{location},{report_date}\n")
        st.success("Reported! Thanks!")
    else:
        st.error("Please enter a symptom and select a location.")

# Update reports
reports_df = pd.read_csv("user_reports.csv")
report_counts = reports_df.groupby(["Date", "Location"]).size().reset_index(name="Report_Count")
daily_summary = daily_summary.drop(columns=["Report_Count"], errors="ignore")
daily_summary = daily_summary.merge(report_counts, on=["Date", "Location"], how="left").fillna({"Report_Count": 0})
daily_summary["Total_Risk"] = daily_summary["Total_Risk"] + daily_summary["Report_Count"] * 10

# --- Phase 3: Scalability ---
# Store past data
if not os.path.exists("past_outbreaks.csv"):
    daily_summary.to_csv("past_outbreaks.csv", index=False)
else:
    past_df = pd.read_csv("past_outbreaks.csv")
    daily_summary = pd.concat([past_df, daily_summary]).drop_duplicates(subset=["Date", "Location"])

# Add coordinates
coords = {
    "Banjara Hills": (17.4108, 78.4376),
    "Gachibowli": (17.4401, 78.3489),
    "Madhapur": (17.4483, 78.3915),
    "Kukatpally": (17.4948, 78.3996),
    "Secunderabad": (17.4399, 78.4983),
    "Hitech City": (17.4416, 78.3804)
}
daily_summary["Latitude"] = daily_summary["Location"].map(lambda x: coords.get(x, (17.3850, 78.4867))[0])
daily_summary["Longitude"] = daily_summary["Location"].map(lambda x: coords.get(x, (17.3850, 78.4867))[1])

# Heatmap
fig = px.scatter_map(
    daily_summary,
    lat="Latitude",
    lon="Longitude",
    size="Total_Risk",
    color="Total_Risk",
    hover_data=["Location", "Date", "Flu_Mentions", "Cases", "Total_Risk"],
    map_style="carto-positron",
    zoom=10,
    title="Flu Risk Heatmap - Hyderabad"
)
st.plotly_chart(fig)

# Alerts
max_risk = daily_summary["Total_Risk"].max()
if max_risk > 50:
    st.warning(f"High Risk Alert! Max risk: {max_risk} detected!")

# Show data
st.subheader("Daily Summary")
st.write(daily_summary)