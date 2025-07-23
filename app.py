
# import pandas as pd
# import spacy
# from sklearn.ensemble import RandomForestClassifier
# import plotly.express as px
# import streamlit as st
# import requests
# from datetime import datetime, timedelta
# import random
# import os

# random.seed(42)

# try:
#     nlp = spacy.load("en_core_web_sm")
# except OSError:
#     st.error("spaCy model not found. Run: python -m spacy download en_core_web_sm")
#     exit(1)

# # --- Phase 1: Prototype ---
# # Mock news dataset
# flu_articles = [
#     "Bird Flu Hits Banjara Hills: 1,000 Birds Culled - Poultry farms scramble.",
#     "Gachibowli Flu Surge: Fever Cases Up 20% - Hospitals busy.",
#     "Madhapur Flu Fears: Chicken Sales Drop - Panic spreads.",
#     "Kukatpally Flu Season Peaks: Coughs Everywhere - Clinics packed.",
#     "Secunderabad Bird Flu: 3,000 Chickens Dead - Alert issued.",
#     "Hitech City Flu Spike: 50 Cases Today - Health dept steps in."
# ]
# noise_articles = [
#     "Banjara Hills Traffic Chaos: No Flu, Just Jams - Roads clogged.",
#     "Gachibowli Rain Woes: Sick of Floods - Weather sucks.",
#     "Madhapur Heatwave: No Outbreak - Summer hits hard."
# ]
# locations = ["Banjara Hills", "Gachibowli", "Madhapur", "Kukatpally", "Secunderabad", "Hitech City"]

# # Generate 200 articles (last 14 days for broader range)
# articles = []
# base_date = datetime.now() - timedelta(days=14)  # Start 14 days ago
# for i in range(200):
#     loc = random.choice(locations)
#     if random.random() < 0.7:
#         text = random.choice(flu_articles).replace("Hyderabad", loc)
#     else:
#         text = random.choice(noise_articles).replace("Hyderabad", loc)
#     date = (base_date + timedelta(days=i//20)).strftime("%Y-%m-%d")
#     articles.append({"Text": text, "Location": loc, "Date": date})

# news_df = pd.DataFrame(articles)

# # Mock flu cases (last 14 days)
# dates = [(datetime.now() - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(14, -1, -1)]  # Last 15 days
# mock_cases = []
# for date in dates:
#     for loc in locations:
#         mock_cases.append({
#             "Date": date,
#             "Cases": random.randint(0, 10),
#             "Location": loc
#         })
# cases_df = pd.DataFrame(mock_cases)

# # Mock weather data (last 14 days)
# mock_weather = {
#     "Date": dates,
#     "Temperature": [28, 30, 25, 22, 26, 29, 27, 28, 30, 24, 23, 26, 29, 27, 28],
#     "Humidity": [40, 35, 50, 60, 45, 40, 55, 50, 38, 52, 58, 47, 42, 53, 49],
#     "Rainfall": [0, 0, 5, 10, 0, 0, 2, 0, 1, 3, 8, 0, 0, 4, 0]
# }
# weather_df = pd.DataFrame(mock_weather)

# news_df.to_csv("mock_news.csv", index=False)
# cases_df.to_csv("mock_cases.csv", index=False)
# weather_df.to_csv("mock_weather.csv", index=False)

# def count_flu_mentions(text):
#     doc = nlp(text.lower())
#     flu_keywords = ["flu", "fever", "cough", "bird flu"]
#     return sum(1 for token in doc if token.text in flu_keywords)

# news_df["Flu_Mentions"] = news_df["Text"].apply(count_flu_mentions)

# all_dates = pd.date_range(start=base_date, end=datetime.now(), freq="D").strftime("%Y-%m-%d").tolist()
# all_combinations = pd.DataFrame(
#     [(d, loc) for d in all_dates for loc in locations],
#     columns=["Date", "Location"]
# )

# daily_summary = news_df.groupby(["Date", "Location"])["Flu_Mentions"].sum().reset_index()
# daily_summary = all_combinations.merge(daily_summary, on=["Date", "Location"], how="left").fillna({"Flu_Mentions": 0})

# daily_summary = daily_summary.merge(cases_df, on=["Date", "Location"], how="left").fillna({"Cases": 0})
# daily_summary = daily_summary.merge(weather_df, on="Date", how="left").fillna({"Temperature": 25, "Humidity": 40, "Rainfall": 0})

# # Basic risk prediction
# daily_summary["Base_Risk"] = daily_summary["Flu_Mentions"] * 5 + daily_summary["Cases"] * 2

# # --- Phase 2: Core Features ---
# # Weather-adjusted risk
# def adjust_risk(row):
#     risk = row["Base_Risk"]
#     if row["Temperature"] < 25:
#         risk += 10
#     if row["Humidity"] > 50:
#         risk += 5
#     if row["Rainfall"] > 0:
#         risk += 5
#     return risk

# daily_summary["Total_Risk"] = daily_summary.apply(adjust_risk, axis=1)

# # Crowdsourcing
# if not os.path.exists("user_reports.csv"):
#     mock_reports = {
#         "Symptom": ["fever", "cough", "flu", "fever", "cough"],
#         "Location": ["Gachibowli", "Madhapur", "Kukatpally", "Hitech City", "Banjara Hills"],
#         "Date": [dates[-5], dates[-4], dates[-3], dates[-2], dates[-1]]
#     }
#     pd.DataFrame(mock_reports).to_csv("user_reports.csv", index=False)

# # --- Streamlit App ---
# # CSS for compact layout
# st.markdown(
#     """
#     <style>
#     .main > div {
#         max-width: 800px;
#         margin: auto;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# st.title("AI Public Health Tracker")
# st.write("Tracking flu outbreaks in Hyderabad with AI!")

# # Crowdsourcing form
# st.header("Report Symptoms")
# symptom = st.text_input("Enter your symptom (e.g., fever, cough):")
# location = st.selectbox("Your location:", locations)
# # Flexible date picker (past 1 year to 1 year ahead)
# today = datetime.now()
# selected_date = st.date_input(
#     "Select date:",
#     value=today,
#     min_value=today - timedelta(days=365),  # 1 year back
#     max_value=today + timedelta(days=365)   # 1 year forward
# )
# if st.button("Submit"):
#     if symptom.strip() and location:
#         report_date = selected_date.strftime("%Y-%m-%d")
#         with open("user_reports.csv", "a") as f:
#             f.write(f"{symptom.strip()},{location},{report_date}\n")
#         st.success("Reported! Thanks!")
#     else:
#         st.error("Please enter a symptom and select a location.")

# # Update reports
# reports_df = pd.read_csv("user_reports.csv")
# report_counts = reports_df.groupby(["Date", "Location"]).size().reset_index(name="Report_Count")
# daily_summary = daily_summary.drop(columns=["Report_Count"], errors="ignore")
# daily_summary = daily_summary.merge(report_counts, on=["Date", "Location"], how="left").fillna({"Report_Count": 0})
# daily_summary["Total_Risk"] = daily_summary["Total_Risk"] + daily_summary["Report_Count"] * 10

# # --- Phase 3: Scalability ---
# # Store past data
# if not os.path.exists("past_outbreaks.csv"):
#     daily_summary.to_csv("past_outbreaks.csv", index=False)
# else:
#     past_df = pd.read_csv("past_outbreaks.csv")
#     daily_summary = pd.concat([past_df, daily_summary]).drop_duplicates(subset=["Date", "Location"])

# # Add coordinates
# coords = {
#     "Banjara Hills": (17.4108, 78.4376),
#     "Gachibowli": (17.4401, 78.3489),
#     "Madhapur": (17.4483, 78.3915),
#     "Kukatpally": (17.4948, 78.3996),
#     "Secunderabad": (17.4399, 78.4983),
#     "Hitech City": (17.4416, 78.3804)
# }
# daily_summary["Latitude"] = daily_summary["Location"].map(lambda x: coords.get(x, (17.3850, 78.4867))[0])
# daily_summary["Longitude"] = daily_summary["Location"].map(lambda x: coords.get(x, (17.3850, 78.4867))[1])

# # Heatmap
# fig = px.scatter_map(
#     daily_summary,
#     lat="Latitude",
#     lon="Longitude",
#     size="Total_Risk",
#     color="Total_Risk",
#     hover_data=["Location", "Date", "Flu_Mentions", "Cases", "Total_Risk"],
#     map_style="carto-positron",
#     zoom=10,
#     title="Flu Risk Heatmap - Hyderabad"
# )
# st.plotly_chart(fig)

# # Alerts
# max_risk = daily_summary["Total_Risk"].max()
# if max_risk > 50:
#     st.warning(f"High Risk Alert! Max risk: {max_risk} detected!")

# # Show data
# st.subheader("Daily Summary")
# st.write(daily_summary)

# Import free libraries for data, UI, and AI
import pandas as pd  # Data handling (DataFrames)
import spacy  # NLP for flu mentions
import streamlit as st  # Web app UI
import requests  # HTTP requests for news and weather
from bs4 import BeautifulSoup  # News scraping
from datetime import datetime, timedelta  # Date handling
import random  # Mock data
import os  # File operations
import tempfile  # Temp files for Streamlit Cloud
import praw  # Reddit API
import plotly.express as px  # Heatmap and graphs
import overpy  # OpenStreetMap for underserved areas
import tweepy

# Set random seed for consistent mock data
random.seed(42)

# Load spaCy model (free, pre-downloaded via setup.sh)
nlp = spacy.load("en_core_web_sm")

# Define Hyderabad locations and coordinates
locations = ["Banjara Hills", "Gachibowli", "Madhapur", "Kukatpally", "Secunderabad", "Hitech City"]
coords = {
    "Banjara Hills": (17.4108, 78.4376), "Gachibowli": (17.4401, 78.3489),
    "Madhapur": (17.4483, 78.3915), "Kukatpally": (17.4948, 78.3996),
    "Secunderabad": (17.4399, 78.4983), "Hitech City": (17.4416, 78.3804)
}

# Data Fetchers (all free)
@st.cache_data(ttl=3600)  # Cache for 1 hour to save API calls
def fetch_news():
    # Scrape flu news from Indian sites (free, no API key)
    sources = [
        {"url": "https://www.siasat.com/?s=flu+Hyderabad", "tag": "h3"},
        {"url": "https://www.thehindu.com/search/?q=flu+Hyderabad", "tag": "h3"},
        {"url": "https://timesofindia.indiatimes.com/topic/flu-Hyderabad", "tag": "h2"}
    ]
    news_items = []
    today = datetime.now().strftime("%Y-%m-%d")
    for source in sources:
        try:
            response = requests.get(source["url"], timeout=5)  # Fetch page
            soup = BeautifulSoup(response.text, "html.parser")  # Parse HTML
            headlines = [h.text.strip() for h in soup.find_all(source["tag"])][:5]  # Top 5 headlines
            for h in headlines:
                if "flu" in h.lower() or "influenza" in h.lower():  # Filter flu-related
                    news_items.append({"Text": h, "Location": "Hyderabad", "Date": today})
        except:
            st.warning(f"Failed to fetch {source['url']}")  # Show warning if site blocks
    if news_items:
        return pd.DataFrame(news_items)  # Return DataFrame
    # Fallback dummy data
    st.warning("News fetch failed, using dummy data.")
    return pd.DataFrame({
        "Text": ["No flu news today"], "Location": ["Hyderabad"], "Date": [today]
    })

@st.cache_data(ttl=3600)
def fetch_reddit_posts():
    # Fetch flu posts from Reddit (free API)
    try:
        reddit = praw.Reddit(
            client_id=st.secrets.get("REDDIT_CLIENT_ID", ""),
            client_secret=st.secrets.get("REDDIT_CLIENT_SECRET", ""),
            user_agent="health_sentinel_v1"
        )
        posts = []
        today = datetime.now().strftime("%Y-%m-%d")
        for sub in ["hyderabad", "india"]:
            for post in reddit.subreddit(sub).search("flu", limit=5):  # Top 5 posts
                if "flu" in post.title.lower() or "influenza" in post.title.lower():
                    posts.append({"Text": post.title, "Location": "Hyderabad", "Date": today})
        if posts:
            return pd.DataFrame(posts)
        return pd.DataFrame()  # Empty if no posts
    except:
        st.warning("Reddit fetch failed, skipping.")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_weather():
    api_key = st.secrets.get("OPENWEATHERMAP_KEY", "default_key")
    if api_key == "default_key":
        st.warning("Weather API key missing, using dummy data.")
        return pd.DataFrame({
            "Date": [datetime.now().strftime("%Y-%m-%d")],
            "Temperature": [25], "Humidity": [40], "Rainfall": [0]
        })
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Hyderabad,IN&appid={api_key}"
    try:
        weather = requests.get(url, timeout=5).json()
        if weather.get("cod") != 200:
            st.warning(f"Weather fetch failed: {weather.get('message', 'Unknown error')}, using dummy data.")
            return pd.DataFrame({
                "Date": [datetime.now().strftime("%Y-%m-%d")],
                "Temperature": [25], "Humidity": [40], "Rainfall": [0]
            })
        return pd.DataFrame({
            "Date": [datetime.now().strftime("%Y-%m-%d")],
            "Temperature": [weather["main"]["temp"] - 273.15],  # Convert Kelvin to Celsius
            "Humidity": [weather["main"]["humidity"]],
            "Rainfall": [weather.get("rain", {}).get("1h", 0)]  # Rainfall in last hour
        })
    except Exception as e:
        st.warning(f"Weather fetch failed: {str(e)}, using dummy data.")
        return pd.DataFrame({
            "Date": [datetime.now().strftime("%Y-%m-%d")],
            "Temperature": [25], "Humidity": [40], "Rainfall": [0]
        })

@st.cache_data(ttl=3600)
def fetch_social_media():
    posts = []
    try:
        # Reddit fetch
        reddit = praw.Reddit(
            client_id=st.secrets.get("REDDIT_CLIENT_ID", ""),
            client_secret=st.secrets.get("REDDIT_CLIENT_SECRET", ""),
            user_agent="health_sentinel"
        )
        subreddit = reddit.subreddit("all")
        for submission in subreddit.search("flu Hyderabad", limit=5):
            posts.append({
                "Text": submission.title + " " + submission.selftext,
                "Location": "Hyderabad",
                "Date": datetime.now().strftime("%Y-%m-%d")
            })
    except Exception as e:
        st.warning(f"Reddit fetch failed: {str(e)}")
    
    try:
        # Twitter v2 fetch
        client = tweepy.Client(
            consumer_key=st.secrets.get("TWITTER_CONSUMER_KEY", ""),
            consumer_secret=st.secrets.get("TWITTER_CONSUMER_SECRET", ""),
            access_token=st.secrets.get("TWITTER_ACCESS_TOKEN", ""),
            access_token_secret=st.secrets.get("TWITTER_ACCESS_TOKEN_SECRET", "")
        )
        tweets = client.search_recent_tweets(query="flu Hyderabad lang:en", max_results=10)
        today = datetime.now().strftime("%Y-%m-%d")
        if tweets.data:
            for tweet in tweets.data:
                posts.append({
                    "Text": tweet.text,
                    "Location": "Hyderabad",
                    "Date": today
                })
    except Exception as e:
        st.warning(f"Twitter fetch failed: {str(e)}, using mock data.")
        today = datetime.now().strftime("%Y-%m-%d")
        posts.extend([
            {"Text": "Flu cases rising in Hyderabad #health", "Location": "Hyderabad", "Date": today},
            {"Text": "Anyone else sick with flu in Hyderabad? 😷", "Location": "Hyderabad", "Date": today}
        ])
    
    if posts:
        return pd.DataFrame(posts)
    st.warning("No social media posts found, using dummy data.")
    return pd.DataFrame({
        "Text": ["Flu cases rising in Hyderabad #health"],
        "Location": ["Hyderabad"],
        "Date": [today]
    })

@st.cache_data(ttl=86400)  # Cache for 1 day
def fetch_underserved_areas():
    # Fetch slum locations in Hyderabad (free OpenStreetMap)
    try:
        api = overpy.Overpass()
        query = """
        [out:json];
        node["place"="slum"](around:10000,17.3850,78.4867);
        out body;
        """
        result = api.query(query)
        return [
            {"Name": n.tags.get("name", "Slum"), "Lat": float(n.lat), "Lon": float(n.lon)}
            for n in result.nodes
        ]
    except:
        st.warning("Failed to fetch underserved areas.")
        return []

# Processing Functions
def count_flu_mentions(text):
    # Count flu keywords using spaCy NLP
    doc = nlp(text.lower())
    flu_keywords = ["flu", "fever", "cough", "bird flu", "influenza"]
    return sum(1 for token in doc if token.text in flu_keywords)

def calculate_trust_score(reports_df, location, date):
    area_reports = reports_df[(reports_df["Location"] == location) & (reports_df["Date"] == date)]
    freq_score = min(len(area_reports) / 10, 1.0)
    symptom_counts = area_reports["Symptom"].value_counts()
    consistency_score = (sum(min(c / len(area_reports), 0.5) for c in symptom_counts) / len(symptom_counts)
                        if not symptom_counts.empty else 0)
    user_score = len(area_reports["User_ID"].unique()) / 5
    return 0.4 * freq_score + 0.4 * consistency_score + 0.2 * user_score

def simulate_cases(news_df, locations):
    # Simulate flu cases based on mentions
    cases = []
    for date in news_df["Date"].unique():
        mentions = news_df[news_df["Date"] == date]["Flu_Mentions"].sum()
        for loc in locations:
            cases.append({
                "Date": date,
                "Cases": random.randint(max(0, int(mentions - 5)), int(mentions + 5)),
                "Location": loc
            })
    return pd.DataFrame(cases)

def forecast_risk(daily_summary, days=7):
    # Forecast risk using exponential moving average
    df = daily_summary.groupby("Date")["Total_Risk"].mean().reset_index()
    df["Forecast"] = df["Total_Risk"].ewm(span=3).mean().shift(-days)
    return df.tail(days)

# Initialize user reports file
reports_file = os.path.join(tempfile.gettempdir(), "user_reports.csv")
if not os.path.exists(reports_file):
    mock_reports = {
        "Symptom": ["fever", "cough", "flu"],
        "Location": ["Gachibowli", "Madhapur", "Kukatpally"],
        "Date": [(datetime.now() - timedelta(days=x)).strftime("%Y-%m-%d") for x in [2, 1, 0]],
        "User_ID": ["user1", "user2", "user3"],
        "Confirmed_Cases": [0, 0, 0]
    }
    pd.DataFrame(mock_reports).to_csv(reports_file, index=False)

# Streamlit App
st.set_page_config(layout="centered", page_title="Health Tracker")  # Center layout
st.markdown("""
<style>
.main {background-color: #1e1e1e; color: #ffffff; font-family: 'Montserrat', sans-serif;}
.stButton>button {background-color: #4CAF50; color: white;}
.stButton>button:hover {background-color: #45a049;}
</style>
""", unsafe_allow_html=True)  # Dark mode, Montserrat font, button hover

st.title("Health Tracker")  # App title
st.caption("Real-Time Disease Defense for Your City")  
# st.image("logo.png", width=100)  # Uncomment if you add a logo

# Report Form
st.header("Report Symptoms or Cases")
symptom = st.text_input("Symptom (e.g., fever, cough)")  # Symptom input
location = st.selectbox("Location", locations)  # Location dropdown
date = st.date_input("Date", value=datetime.now(), min_value=datetime.now() - timedelta(days=365))  # Date picker
cases = st.number_input("Confirmed Cases (if known)", min_value=0)  # Case reporting
user_id = st.text_input("User ID (e.g., email, anonymous)", value=f"user{random.randint(1000, 9999)}")  # Random user ID
if st.button("Submit Report"):
    if symptom.strip() or cases > 0:
        report_date = date.strftime("%Y-%m-%d")
        with open(reports_file, "a") as f:
            f.write(f"{symptom},{location},{report_date},{user_id},{cases}\n")  # Save report
        st.success("Report submitted! 🎉")  # Success with emoji
    else:
        st.error("Enter a symptom or case count.")  # Error if empty

# Fetch Data
news_df = pd.concat([fetch_news(), fetch_social_media(), fetch_reddit_posts()], ignore_index=True)  # Combine data
news_df["Flu_Mentions"] = news_df["Text"].apply(count_flu_mentions)  # Count mentions
cases_df = simulate_cases(news_df, locations)  # Simulate cases
weather_df = fetch_weather()  # Fetch weather
reports_df = pd.read_csv(reports_file)  # Load user reports
report_counts = reports_df.groupby(["Date", "Location"]).size().reset_index(name="Report_Count")  # Count reports
case_counts = reports_df.groupby(["Date", "Location"])["Confirmed_Cases"].sum().reset_index()  # Sum cases

# Build Summary
all_dates = pd.date_range(start=datetime.now() - timedelta(days=14), end=datetime.now(), freq="D").strftime("%Y-%m-%d")
all_combinations = pd.DataFrame([(d, loc) for d in all_dates for loc in locations], columns=["Date", "Location"])
daily_summary = all_combinations.merge(
    news_df.groupby(["Date", "Location"])["Flu_Mentions"].sum().reset_index(), how="left"
).fillna({"Flu_Mentions": 0})
daily_summary = daily_summary.merge(cases_df, how="left").fillna({"Cases": 0})
daily_summary = daily_summary.merge(weather_df, how="left").fillna({"Temperature": 25, "Humidity": 40, "Rainfall": 0})
daily_summary = daily_summary.merge(report_counts, how="left").fillna({"Report_Count": 0})
daily_summary = daily_summary.merge(case_counts, how="left").fillna({"Confirmed_Cases": 0})

# Calculate Trust Scores
daily_summary["Trust_Score"] = daily_summary.apply(
    lambda row: calculate_trust_score(reports_df, row["Location"], row["Date"]), axis=1
)

# Identify Underserved Areas
underserved_areas = fetch_underserved_areas()
daily_summary["Is_Underserved"] = daily_summary.apply(
    lambda row: any(abs(row["Latitude"] - area["Lat"]) < 0.01 and abs(row["Longitude"] - area["Lon"]) < 0.01 for area in underserved_areas), axis=1
)

# Calculate Risk
daily_summary["Base_Risk"] = daily_summary["Flu_Mentions"] * 5 + daily_summary["Cases"] * 2 + daily_summary["Confirmed_Cases"] * 10
daily_summary["Total_Risk"] = daily_summary.apply(
    lambda row: row["Base_Risk"] + (
        10 if row["Temperature"] < 25 else 0) + (
        5 if row["Humidity"] > 50 else 0) + (
        5 if row["Rainfall"] > 0 else 0) + (
        row["Report_Count"] * 5 if row["Trust_Score"] > 0.7 else 0) + (
        row["Base_Risk"] * 0.5 if row["Is_Underserved"] else 0), axis=1
)

def get_prevention_alert(location, risk, weather):
    tips = []
    if risk > 50:
        tips.append("Wear masks in public.")
    if weather["Rainfall"] > 0:
        tips.append("Boil drinking water.")
    if weather["Temperature"] < 25:
        tips.append("Keep warm to avoid flu.")
    return f"{location}: {' '.join(tips)}" if tips else f"{location}: Stay vigilant."

daily_summary["Alert"] = daily_summary.apply(
    lambda row: get_prevention_alert(row["Location"], row["Total_Risk"], {
        "Rainfall": row["Rainfall"], "Temperature": row["Temperature"]
    }), axis=1
)

# Dashboard
st.header("Risk Forecasting Dashboard")
daily_summary["Latitude"] = daily_summary["Location"].map(lambda x: coords.get(x)[0])
daily_summary["Longitude"] = daily_summary["Location"].map(lambda x: coords.get(x)[1])
fig = px.scatter_map(
    daily_summary, lat="Latitude", lon="Longitude", size="Total_Risk", color="Total_Risk",
    hover_data=["Location", "Date", "Flu_Mentions", "Cases", "Total_Risk", "Trust_Score", "Alert"],
    map_style="carto-positron", zoom=10, title="Flu Risk Heatmap"
)
st.plotly_chart(fig)

st.subheader("7-Day Risk Forecast")
forecast_df = forecast_risk(daily_summary)
st.plotly_chart(px.line(forecast_df, x="Date", y="Forecast", title="Predicted Risk"))

st.subheader("Historical Trends")
trend_df = daily_summary.groupby("Date")["Total_Risk"].mean().reset_index()
st.plotly_chart(px.line(trend_df, x="Date", y="Total_Risk", title="Risk Over Time"))

# Alerts
for _, row in daily_summary.iterrows():
    if row["Total_Risk"] > 50:
        if row["Is_Underserved"]:
            st.error(f"CRITICAL: {row['Alert']} (Underserved Area, Trust Score: {row['Trust_Score']:.2f})")
        else:
            st.warning(f"ALERT: {row['Alert']} (Trust Score: {row['Trust_Score']:.2f})")

# Debug Data (optional, comment out for demo)
st.subheader("Data Summary")
st.write(daily_summary)
