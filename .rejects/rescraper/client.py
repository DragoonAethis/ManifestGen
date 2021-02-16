import praw
from credentials import *


credentials = {}
if USE_CREDENTIALS:
    credentials['username'] = USERNAME
    credentials['password'] = PASSWORD

    if REQUEST_2FA:
        token = input("2FA code: ")
        credentials['password'] = f"{PASSWORD}:{token}"


reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=CLIENT_USER_AGENT,
    **credentials
)

if not USE_CREDENTIALS:
    reddit.read_only = True
