# main.py
import twikit
from data_fetching import fetch_and_display_top_tweets, fetch_top_replies, fetch_user_stats
from services import load_initial_stats_from_csv, save_stats_to_csv, write_most_liked_data_to_csv, write_data_to_csv, initialize_csv_files, initialize_most_liked_csv_file, write_most_retweeted_data_to_csv
from data import SOCIAL_MEDIA_ACCOUNTS, TEAM_MEMBERS
from config import BOT_TOKEN, CHAT_ID, ADMIN_CHAT_ID, EDRIAN_CHAT_ID, LYNNETH_CHAT_ID, SHEILA_CHAT_ID, JESS_CHAT_ID, JOHN_CHAT_ID, LIZ_CHAT_ID, RAINE_CHAT_ID
from data_fetching import fetch_and_display_top_tweets, fetch_top_replies, fetch_user_stats
from services import load_initial_stats_from_csv, save_stats_to_csv, write_most_liked_data_to_csv, write_most_retweeted_data_to_csv
from data import SOCIAL_MEDIA_ACCOUNTS, TEAM_MEMBERS
from config import BOT_TOKEN, CHAT_ID, ADMIN_CHAT_ID, USERNAME, EMAIL, PASSWORD
from utils import login_and_save_cookies, initialize_client, get_worker_for_date, day_of_week_in_range
from config import CSV_FILE_PATH, MOST_LIKED_CSV_FILE_PATH, COOKIES_PATH, CONFIG_PATH
import asyncio
import logging
from telegram import Update
from telegram.helpers import escape_markdown
from twikit import Client, TooManyRequests
from datetime import datetime, timedelta
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
import re

application = None

async def check_login_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client = await initialize_client()  # Assuming this function returns a client configured with your cookies
    try:
        # Try to perform an operation that requires authentication
        user_info = await fetch_user_stats(client, 'elonmusk') 
        if user_info:
            message = "Logged in successfully. Cookies are working."
        else:
            message = "Failed to log in. Cookies might not be working."
    except Exception as e:
        message = f"Failed to log in with error: {e}"

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)


async def send_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id  # Retrieve the chat ID from the update object
    await context.bot.send_message(chat_id=chat_id, text=f"The chat ID is: {chat_id}")


# Command to show how long each employee has been working
async def howlongworking(update, context):
    now = datetime.now()
    response = "Employee Work Duration:\n"
    for member_name, info in TEAM_MEMBERS.items():
        start_date = info['start_date']
        duration = now - start_date
        days_worked = duration.days
        years, remainder = divmod(days_worked, 365)
        months = remainder // 30

        if days_worked < 90:  # If less than 3 months, show days worked
            response += f"- {member_name}: {days_worked} days\n"
        else:
            response += f"- {member_name}: {years} years, {months} months\n"

    await context.bot.send_message(chat_id=CHAT_ID, text=response)

async def daily_initial_stats():
    print("daily_initial_stats() running...")
    client = await initialize_client()
    current_day = datetime.now(pytz.timezone('Asia/Manila'))
    formatted_current_day = current_day.strftime('%A, %B %d, %Y')
    print("Current day = " + formatted_current_day)
    message = f"*Happy {formatted_current_day} everyone!*\n\n"

    # Fetch morning stats
    for account, workers in SOCIAL_MEDIA_ACCOUNTS.items():
        worker_today = get_worker_for_date(account, current_day)
        user_stats = await fetch_user_stats(client, account.lstrip('@'))
        if user_stats:
            # Update account_stats with morning data
            account_stats[account] = {
                'initial_followers': user_stats['followers_count'],
                'initial_tweets': user_stats['tweets_count']
            }
            message += f"*{account}*\n"
            message += f"*Followers*: {user_stats['followers_count']}\n"
            message += f"*Tweet Count*: {user_stats['tweets_count']}\n"
            message += f"_Good luck today, {worker_today}_!\n\n"

    # Save the morning stats to CSV
    save_stats_to_csv(account_stats, CSV_FILE_PATH)
    await application.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, parse_mode='Markdown')



from datetime import datetime
import pytz

async def daily_followers_gained():
    print("daily_followers_gained() running...")
    client = await initialize_client()
    date_today = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d')
    summary_header = f"**Daily Summary for {date_today}**\n\n"
    account_summaries = []

    updated_stats = {}  # Structure to store updated stats for future use

    for account in SOCIAL_MEDIA_ACCOUNTS.keys():
        try:
            user_stats = await fetch_user_stats(client, account.lstrip('@'))
            if user_stats:
                initial_followers = account_stats[account]['initial_followers']
                initial_tweets = account_stats[account]['initial_tweets']
                final_followers = user_stats['followers_count']
                final_tweets = user_stats['tweets_count']

                followers_gain = final_followers - initial_followers
                tweets_added = final_tweets - initial_tweets

                account_summary = (
                    f"**Account:** *{account}*\n"
                    f"**Followers Gained:** {followers_gain} "
                    f"(Initial: {initial_followers}, Final: {final_followers})\n"
                    f"**Tweets Added:** {tweets_added} "
                    f"(Initial: {initial_tweets}, Final: {final_tweets})\n"
                    f"---------------------------\n"
                )
                account_summaries.append(account_summary)

                # Update the stats for the account
                updated_stats[account] = {
                    'initial_followers': followers_gain,
                    'initial_tweets': tweets_added
                }
            else:
                account_summaries.append(f"**Account:** *{account}* - Unable to fetch stats for today.\n\n")
        except Exception as e:
            account_summaries.append(f"**Account:** *{account}* - Error occurred: {str(e)}\n\n")
            continue

    # Combine header and account summaries
    full_message = summary_header + "".join(account_summaries)
    await application.bot.send_message(chat_id=CHAT_ID, text=full_message, parse_mode='Markdown')
    print("saving stats to csv...")
    save_stats_to_csv(updated_stats, CSV_FILE_PATH)

# Remove `context` parameter
async def send_top_replies_message():
    await fetch_and_display_top_tweets(
        application.bot, "Likes", "favorite_count", "Liked",
        write_most_liked_data_to_csv, is_fav=True
    )

async def send_top_retweeted_message():
    await fetch_and_display_top_tweets(
        application.bot, "Retweets", "retweet_count", "Retweeted",
        write_most_retweeted_data_to_csv, is_fav=False
    )



# Function to handle commands invoked through /anonymous
async def invoke_command_via_anonymous(context, command, args):
    command_mapping = {
        "howlongworking": howlongworking,
        "pay": pay,
    }

    # Create a mock Update object with the group chat ID for context
    class MockUpdate:
        def __init__(self, chat_id):
            self.message = type('obj', (object,), {'chat_id': chat_id})

    if command in command_mapping:
        # Use the group chat ID in the mock update
        mock_update = MockUpdate(CHAT_ID)
        await command_mapping[command](mock_update, context)

# Command to handle anonymous messages
async def anonymous(update, context):
    # Check if there are any arguments provided
    if context.args:
        # Join the message parts together
        anonymous_message = ' '.join(context.args)
        # Format the message as "ANON: {message}"
        formatted_message = f"ANON: {anonymous_message}"

        # Send the formatted message to the public group chat
        await context.bot.send_message(chat_id=CHAT_ID, text=formatted_message)

        # Get the sender's username
        sender_username = update.message.from_user.username if update.message.from_user.username else "Unknown User"
        # Format the admin message with username and original message
        admin_message = f"Anonymous message sent by @{sender_username}: {anonymous_message}"

        # Send the admin message to your personal chat
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

        # Check if the anonymous message starts with a command
        if anonymous_message.startswith("/"):
            # Split the message into command and arguments
            command, *args = anonymous_message[1:].split()
            # Manually invoke the command handler for the group chat
            await invoke_command_via_anonymous(context, command, args)
    else:
        # If no message is provided, send a prompt asking for a message
        await update.message.reply_text("Please provide a message to send anonymously. Usage: /anonymous <message>")

# Command handlers
async def initial_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await daily_initial_stats()

async def followers_gained(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await daily_followers_gained()

async def mostliked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_top_replies_message()

async def mostretweeted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_top_retweeted_message()

# Function to calculate the next payday (every two weeks on Friday)
def get_next_payday():
    today = datetime.now()
    days_until_next_friday = (4 - today.weekday()) % 7  # Calculate days until next Friday
    next_friday = today + timedelta(days=days_until_next_friday)

    # Check if this Friday is a payday (every 2 weeks from August 2nd)
    reference_date = datetime(2024, 8, 2)  # Set the reference payday (e.g., August 2)
    if (next_friday - reference_date).days % 14 != 0:
        next_friday += timedelta(days=7)

    days_until_payday = (next_friday - today).days
    return next_friday, days_until_payday

# Command to show when the next payday is
async def pay(update, context):
    next_payday, days_until_payday = get_next_payday()
    response = f"Pay is in {days_until_payday} days from now, on {next_payday.strftime('%A, %B %d')}."
    await context.bot.send_message(chat_id=CHAT_ID, text=response)

def schedule_anniversaries_and_birthdays(scheduler):
    current_year = datetime.now().year
    for member_name, info in TEAM_MEMBERS.items():
        start_date = info['start_date']
        birthday = info['birthday'].replace(year=current_year)

        # Schedule birthday messages
        if birthday > datetime.now():
            scheduler.add_job(scheduled_birthday_message, 'date', run_date=birthday, args=[member_name])

        # Schedule work anniversaries
        for years in range(1, 11):  # Assuming we want to schedule up to 10 years
            anniversary_date = start_date + timedelta(days=years*365)
            if anniversary_date > datetime.now():
                scheduler.add_job(scheduled_anniversary_message, 'date', run_date=anniversary_date, args=[member_name, years])

# Function to send anniversary message
async def scheduled_anniversary_message(member_name, years):
    application = Application.builder().token(BOT_TOKEN).build()
    await application.bot.send_message(chat_id=CHAT_ID, text=f"Happy {years}-year anniversary, {member_name}! 🎉")

# Function to send birthday message
async def scheduled_birthday_message(member_name):
    application = Application.builder().token(BOT_TOKEN).build()
    await application.bot.send_message(chat_id=CHAT_ID, text=f"Happy Birthday, {member_name}! 🎂")

# PROJECT FEATURE: Function to list the account with the highest liked tweets, and their current streak
async def streak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    application = Application.builder().token(BOT_TOKEN).build()
    message = "@user12923 had the most liked tweet for 2 days in a row! ️ Keep it up! 🔥️‍🔥"
    await context.bot.send_message(chat_id=CHAT_ID, text=message)

# Main function to run the bot
def main():
  global application
  application = Application.builder().token(BOT_TOKEN).connect_timeout(30).build()

  global account_stats
  account_stats = load_initial_stats_from_csv(CSV_FILE_PATH)
  # Initialize CSV file
  initialize_csv_files()
  initialize_most_liked_csv_file()


  # Add command handlers for testing
  application.add_handler(CommandHandler("initial_stats", daily_initial_stats))
  application.add_handler(CommandHandler("followers_gained", daily_followers_gained))
  application.add_handler(CommandHandler("mostliked", mostliked))
  application.add_handler(CommandHandler("mostretweeted", mostretweeted))
  application.add_handler(CommandHandler("anonymous", anonymous))
  application.add_handler(CommandHandler("chatid", send_chat_id))
  application.add_handler(CommandHandler("islogged", check_login_status))
  application.add_handler(CommandHandler("howlong", howlongworking))
  application.add_handler(CommandHandler("pay", pay))
  application.add_handler(CommandHandler('streak', streak_command))

  # Create scheduler for scheduled messages with Philippine Time (PHT)
  scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Manila'))
  schedule_anniversaries_and_birthdays(scheduler)
  # Schedule morning and evening messages in PHT

  # Using application.create_task() to schedule a task
  scheduler.add_job(send_top_replies_message, 'cron', hour=10, minute=0)
  # scheduler.add_job(send_top_retweeted_message, 'cron', hour=10, minute=0)op=pyt
  scheduler.add_job(daily_followers_gained, 'cron', hour=8, minute=0)  
  scheduler.add_job(daily_initial_stats, 'cron', hour=8, minute=0, second=10)
  print("Scheduler added all jobs")


  scheduler.start()
  application.run_polling()

if __name__ == "__main__":
  main()