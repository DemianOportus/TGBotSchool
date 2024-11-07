from datetime import datetime, timedelta
import logging
import re
import pytz
from telegram.ext import ContextTypes
from config import ADMIN_CHAT_ID, CHAT_ID
from data import SOCIAL_MEDIA_ACCOUNTS
from utils import initialize_client, get_worker_for_date
from telegram.helpers import escape_markdown

# Const for minimum queries
MIN_FAVES = 50
MIN_RETWEETS = 10

async def fetch_user_stats(client, username):
    try:
        user = await client.get_user_by_screen_name(username)
        if user:
            return {
                'name': user.name,
                'followers_count': user.followers_count,
                'tweets_count': user.statuses_count
            }
        else:
            print(f"No user found for {username}")
            return None
    except Exception as e:
        print(f"Error fetching data for {username}: {e}")
        return None


async def fetch_top_replies(client, username, specified_date, is_fav=True):
    today_pht = datetime.strptime(specified_date, '%Y-%m-%d').astimezone(pytz.timezone('Asia/Manila'))
    end_date = (today_pht + timedelta(days=1)).strftime('%Y-%m-%d')

    # Construct query based on whether we are fetching by likes or retweets
    if is_fav:
        query = f'(from:{username}) min_faves:{MIN_FAVES} lang:en until:{end_date} since:{specified_date} filter:replies'
    else:
        query = f'(from:{username}) min_retweets:{MIN_RETWEETS} lang:en until:{end_date} since:{specified_date} filter:replies'

    try:
        tweets = await client.search_tweet(query, product='Top')
        if not tweets:
            print(f"No tweets found for {username} with query {query}")
            return []

        # Sort by either favorite_count or retweet_count depending on is_fav
        if is_fav:
            sorted_tweets = sorted(tweets, key=lambda x: x.favorite_count, reverse=True)
        else:
            sorted_tweets = sorted(tweets, key=lambda x: x.retweet_count, reverse=True)

        return sorted_tweets[:3]  # Get top 3 replies
    except Exception as e:
        print(f"Error fetching top replies for {username}: {e}")
        return []

async def fetch_and_display_top_tweets(bot, stat_type, stat_key, message_title, write_to_csv_func, is_fav=True):
    client = await initialize_client()
    yesterday_pht = (datetime.now(pytz.timezone('Asia/Manila')) - timedelta(days=1))
    day_yesterday = yesterday_pht.strftime('%A')
    date_yesterday = yesterday_pht.strftime('%Y-%m-%d')

    message = f"*{escape_markdown(day_yesterday)}: Top 3 Most {escape_markdown(message_title)} Tweets!*\n\n"

    for account, workers in SOCIAL_MEDIA_ACCOUNTS.items():
        user_stats = await fetch_user_stats(client, account.lstrip('@'))
        if user_stats:
            account_name = user_stats.get('name', "Unknown Account")
        else:
            account_name = "Unknown Account"
            print(f"Failed to fetch user stats for {account}.")


        top_tweets = await fetch_top_replies(client, account.lstrip('@'), date_yesterday, is_fav=is_fav)
        worker_yesterday = str(get_worker_for_date(account, yesterday_pht) or "Unknown Worker")

        message += f"--------*{escape_markdown(worker_yesterday)}* on *{escape_markdown(account_name)}*'s top tweets:\n"

        if top_tweets:
            for i, tweet in enumerate(top_tweets[:3]):  # Ensure we only iterate over the actual tweets
                tweet_created_at = datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S %z %Y')
                tweet_url = f"https://x.com/{account.lstrip('@')}/status/{tweet.id}"

                # Clean tweet text by removing URLs and handles
                tweet_text = re.sub(r'http\S+', '', tweet.text).strip()
                tweet_text = re.sub(r'@\w+', '', tweet_text).strip()

                # Escape markdown characters
                escaped_tweet_text = escape_markdown(tweet_text)

                # Append message
                message += f"{i + 1}. {escaped_tweet_text}\n"
                message += f"{stat_type}: {getattr(tweet, stat_key)} [View Tweet]({tweet_url})\n\n"

                # Save the data to CSV only once per valid tweet
                write_to_csv_func(date_yesterday, account_name, tweet_text, getattr(tweet, stat_key), worker_yesterday)

            # Fill remaining slots with "Unfortunately" if fewer than 3 tweets were found
            for i in range(len(top_tweets), 3):
                message += f"{i + 1}. Unfortunately, {escape_markdown(worker_yesterday)} didn't get any more tweets with the required {stat_type} yesterday!\n\n"
        else:
            # No tweets at all, so output the "Unfortunately" messages 3 times
            for i in range(3):
                message += f"{i + 1}. Unfortunately, {escape_markdown(worker_yesterday)} didn't get any tweets with the required {stat_type} yesterday!\n\n"

    try:
        logging.info(f"Sending message to chat ID {ADMIN_CHAT_ID}")
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message.strip(),
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        logging.info("Message sent successfully")
    except Exception as e:
        logging.error(f"Failed to send message: {e}")

