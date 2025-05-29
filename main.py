import os
from dotenv import load_dotenv
import tweepy
import requests
import schedule
import time
import logging
import datetime

# Load environment variables from .env file
load_dotenv()

# Twitter API credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# OpenWeatherMap API key
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Set up logging
logging.basicConfig(filename='weather_bot.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Tweepy Client (API v2)
client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET
)

def get_weather():
    """Fetch min and max temperatures for today in Guatemala City from OpenWeatherMap."""
    city = "Guatemala City"
    url = (f"https://api.openweathermap.org/data/2.5/forecast?"
           f"q={city}&appid={OPENWEATHER_API_KEY}&units=metric")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        temps_today = []
        
        for entry in data["list"]:
            dt_txt = entry["dt_txt"]  # e.g. "2025-03-05 06:00:00"
            if dt_txt.startswith(today_str):
                temps_today.append(entry["main"]["temp"])
        
        if not temps_today:
            logging.error("No forecast data found for today.")
            return None, None
        
        min_temp = min(temps_today)
        max_temp = max(temps_today)
        return min_temp, max_temp
    except Exception as e:
        logging.error(f"Error fetching weather: {e}")
        return None, None

def post_weather():
    """Create and post a tweet with today's min and max temperatures."""
    min_temp, max_temp = get_weather()
    if min_temp is None or max_temp is None:
        logging.error("Skipping tweet due to weather fetch error.")
        return
    
    tweet_text = (
        f"Buenos días! Temperatura de hoy en Ciudad de Guatemala:\n"
        f"Mín: {min_temp:.1f}°C, Máx: {max_temp:.1f}°C. #climagt"
    )
    
    try:
        response = client.create_tweet(text=tweet_text)
        logging.info(f"Tweet posted successfully! Tweet ID: {response.data['id']}")
    except Exception as e:
        logging.error(f"Error posting tweet: {e}")

# Schedule the task daily at 6:00 AM
schedule.every().day.at("06:00").do(post_weather)

print("Weather bot running...")

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)

#     # For testing
# post_weather()