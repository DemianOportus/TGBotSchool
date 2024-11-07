# data.py
from datetime import datetime
from config import EDRIAN_CHAT_ID, LYNNETH_CHAT_ID, SHEILA_CHAT_ID, JESS_CHAT_ID, JOHN_CHAT_ID, LIZ_CHAT_ID, RAINE_CHAT_ID

# Team Members' Information
TEAM_MEMBERS = {
    'Chris': {'start_date': datetime(2023, 7, 10), 'birthday': datetime(2024, 9, 5)},
    'Jess': {'start_date': datetime(2024, 7, 8), 'birthday': datetime(2024, 5, 1)},
    'Edrian K': {'start_date': datetime(2024, 7, 16), 'birthday': datetime(2024, 4, 18)},
    'Liz': {'start_date': datetime(2024, 7, 17), 'birthday': datetime(2024, 11, 28)},
    'Raine': {'start_date': datetime(2024, 8, 3), 'birthday': datetime(2024, 10, 16)},
    'John': {'start_date': datetime(2024, 8, 4), 'birthday': datetime(2024, 6, 30)},
    'Sheila': {'start_date': datetime(2024, 8, 24), 'birthday': datetime(1996, 4, 20)},
    'Lynneth': {'start_date': datetime(2024, 8, 30), 'birthday': datetime(2024, 9, 18)}
}

# Social Media Accounts and corresponding chat IDs and usernames
SOCIAL_MEDIA_ACCOUNTS = {
    '@imcoolchristian': {
        'Jess': ('Mon-Fri', JESS_CHAT_ID),
        'Lynneth': ('Sat-Sun', LYNNETH_CHAT_ID)
    },
    '@MasculineBased': {
        'Edrian K': ('Mon-Sat', EDRIAN_CHAT_ID)
    },
    '@UsuallyPregnant': {
        'Liz': ('Mon-Fri', LIZ_CHAT_ID),
        'Raine': ('Sat-Sun', RAINE_CHAT_ID)
    },
    '@OneXOneY': {
        'John': ('Mon-Fri', JOHN_CHAT_ID),
        'Sheila': ('Sat-Sun', SHEILA_CHAT_ID)
    }
}


