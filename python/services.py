# Services.py
from datetime import datetime
import logging
import os
import csv
import pandas as pd
import pytz
from config import MOST_LIKED_CSV_FILE_PATH, CSV_FILE_PATH, MOST_RETWEETED_CSV_FILE_PATH

# Basic logging configuration
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

# Reduce the logging verbosity for APScheduler and httpx
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

def write_most_liked_data_to_csv(date, account_name, tweet_text, likes, posted_by):
    try:
        with open(MOST_LIKED_CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([date, account_name, tweet_text, likes, posted_by])
    except Exception as e:
        logging.error(f"Failed to write to most liked CSV: {e}")

def write_data_to_csv(date, account_name, followers_gain, tweets_added):
    try:
        with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([date, account_name, followers_gain, tweets_added])
    except Exception as e:
        logging.error(f"Failed to write to data CSV: {e}")

def write_most_retweeted_data_to_csv(date, account_name, tweet_text, retweets, posted_by):
    """Save the most retweeted tweets data to the CSV."""
    try:
        with open(MOST_RETWEETED_CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([date, account_name, tweet_text, retweets, posted_by])
    except Exception as e:
        logging.error(f"Failed to write to most retweeted CSV: {e}")

def initialize_csv_files():
    try:
        if not os.path.exists(MOST_LIKED_CSV_FILE_PATH):
            with open(MOST_LIKED_CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Date', 'Account', 'Tweet_Text', 'Likes', 'Posted_By'])
        if not os.path.exists(CSV_FILE_PATH):
            with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Date', 'Account', 'Followers Gained', 'Tweets Added'])
    except Exception as e:
        logging.error(f"Failed to initialize CSV files: {e}")

def initialize_most_liked_csv_file():
    try:
        if not os.path.exists(MOST_LIKED_CSV_FILE_PATH):
            with open(MOST_LIKED_CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Date', 'Account', 'Tweet_Text', 'Likes', 'Posted_By'])
    except Exception as e:
        logging.error(f"Failed to initialize most liked CSV file: {e}")

def load_initial_stats_from_csv(file_path):
    initial_stats = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Ensure handle format is used uniformly
                account = row['Account'].strip()
                if not account.startswith('@'):
                    account = '@' + account
                initial_stats[account] = {
                    'initial_followers': int(row['Followers Gained']),
                    'initial_tweets': int(row['Tweets Added'])
                }
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
    return initial_stats


def save_stats_to_csv(stats, file_path):
    try:
        # Load existing data
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
        else:
            df = pd.DataFrame(columns=['Date', 'Account', 'Followers Gained', 'Tweets Added'])

        # Update or append new data
        date_today = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d')
        for account, data in stats.items():
            # Remove any existing rows for this account and date
            df = df[~((df['Date'] == date_today) & (df['Account'] == account))]

            # Create new row with updated stats
            new_row = {
                'Date': date_today,
                'Account': account,
                'Followers Gained': data['initial_followers'],
                'Tweets Added': data['initial_tweets']
            }

            # Append the new row
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # Debug: Print DataFrame before saving
        print(f"Data being saved to CSV: \n{df.tail()}")

        # Save back to CSV
        df.to_csv(file_path, index=False)

    except Exception as e:
        logging.error(f"Failed to save data to CSV: {e}")




