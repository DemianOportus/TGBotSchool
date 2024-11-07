# utils.py

from twikit import Client
from config import COOKIES_PATH, USERNAME, EMAIL, PASSWORD
import logging
import asyncio
from data import SOCIAL_MEDIA_ACCOUNTS

# Function to handle login and save cookies
async def login_and_save_cookies(client):
    try:
        await client.login(auth_info_1=USERNAME, auth_info_2=EMAIL, password=PASSWORD)
        client.save_cookies(COOKIES_PATH)
        print("Successfully logged in and saved cookies.")
    except Exception as e:
        logging.error(f"Login failed: {e}")
        print(f"Login failed: {e}")

# Function to initialize the client and manage cookies
async def initialize_client():
    client = Client(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    )
    try:
        client.load_cookies(COOKIES_PATH)
        print("Cookies loaded successfully.")
    except Exception as e:
        print(f"Failed to load cookies: {e}")
        await login_and_save_cookies(client)  # Attempt login if loading cookies fails
    return client

# Helper function to get the worker for a specific date
def get_worker_for_date(account, date):
    day_of_week = date.strftime('%a')  # Get the abbreviated day of the week (Mon, Tue, etc.)
    account_info = SOCIAL_MEDIA_ACCOUNTS.get(account, {})

    for worker, (days, chat_id) in account_info.items():
        days_list = days.split(',')
        for day_range in days_list:
            if '-' in day_range:
                start_day, end_day = day_range.split('-')
                if day_of_week_in_range(day_of_week, start_day, end_day):
                    return worker
            elif day_of_week == day_range:
                return worker
    return None

def day_of_week_in_range(day, start, end):
    """ Check if the day is within the start and end day range. """
    week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    start_index = week_days.index(start)
    end_index = week_days.index(end)
    if start_index <= end_index:
        return day in week_days[start_index:end_index+1]
    else:  # the range wraps around the week
        return day in week_days[start_index:] or day in week_days[:end_index+1]
