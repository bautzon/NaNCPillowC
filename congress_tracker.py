import tweepy
import requests
import os
import pandas as pd
import schedule
import time

# Load API Keys from Environment Variables
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")


TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

# Authenticate with Twitter
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Fetch latest congressional trades
def get_congress_trades():
    url = "https://api.quiverquant.com/beta/live/congresstrading"
    headers = {"Authorization": f"Bearer {QUIVER_API_KEY}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        print("Error fetching data:", response.text)
        return pd.DataFrame()

# Filter large trades (> $500K)
def filter_large_trades(df, threshold=500000):
    df["Transaction Amount"] = df["Amount"].astype(float)
    return df[df["Transaction Amount"] > threshold]

# Send tweet alerts
def tweet_trade(trade):
    tweet = f"This Nigga  {trade['Representative']} just bought {trade['Transaction Amount']:,.2f} \n" \
            f" do"
            f"📌 Official: {trade['Representative']}\n" \
            f"📈 Stock: {trade['Ticker']}\n" \
            f"💰 Amount: ${trade['Transaction Amount']:,.2f}\n" \
            f"📅 Date: {trade['Transaction Date']}\n" \
            f"#InsiderTrading #StockTrades #Congress"

    api.update_status(tweet)
    print(f"Tweeted: {tweet}")

# Run the tracker
def run_tracker():
    df = get_congress_trades()
    if not df.empty:
        large_trades = filter_large_trades(df)
        for _, trade in large_trades.iterrows():
            tweet_trade(trade)

# Schedule to run every hour
schedule.every(1).hour.do(run_tracker)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
