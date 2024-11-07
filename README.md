# Social Media Monitoring Bot

## Overview
This Python-based Telegram bot facilitates the monitoring and interaction of designated social media accounts. It provides automated messages to a specified chat based on the activity and statistics of these accounts. Key features include daily updates on follower and tweet counts, handling of the most liked tweets, and user authentication via saved cookies.

## Features
- **Daily Reports**: Sends morning and evening summaries of social media account statistics.
- **Top Replies**: Fetches and reports the top 3 most liked replies from specified accounts.
- **Authentication Check**: Verifies the functionality of stored login cookies.
- **Anonymous Messaging**: Supports sending messages anonymously within the chat.
- **Chat ID Retrieval**: Quickly fetch and display the current chat ID.

## Setup
### Requirements
- Python 3.8+
- `twikit` Python library
- `python-telegram-bot` Python library
- `APScheduler`
- `pytz`

### Installation
1. Clone the repository:

2. Install required Python packages in requirements.txt 
```bash
pip install -r requirements.txt
``` 

### Configuration
- **Bot Token and Chat IDs**: Set your bot's token and relevant chat IDs in the script.
- **Social Media Accounts**: Configure the accounts you wish to monitor in the `SOCIAL_MEDIA_ACCOUNTS` dictionary within the script.

## Usage
### Running the Bot
Execute the bot using the following command:
```bash
python main.py
```

## Interacting with the Bot
- Send `/morningtest` to get the morning report manually.
- Send `/eveningtest` to get the evening report manually.
- Send `/mostliked` to fetch the top 3 most liked replies for the previous day.
- Send `/anonymous [message]` to post a message anonymously.
- Send `/chatid` to retrieve the current chat ID.
- Send `/islogged` to check if the bot is logged in and cookies are functioning.

## Scheduling
The bot uses APScheduler with timezone support for scheduled tasks:
- Morning messages are scheduled for 8 AM, Philippine Time.
- Top Posts are scheduled for 10 AM, Philippine Time.
- Adjustments can be made in the script for scheduling other tasks or changing existing schedules.

## Contributing
Contributions to the bot are welcome. Please fork the repository and submit pull requests with your suggested changes.

## License
X. Corp
