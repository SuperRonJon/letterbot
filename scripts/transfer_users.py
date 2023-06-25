import re
import pickle

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from letterbot.user import User
from letterbot.user_management import add_user_to_channel

followed_users = []

with open('followed.pkl', 'rb') as f:
    followed_users = pickle.load(f)

for user in followed_users:
    print(user.rss_url)
    letterboxd_username = re.search(r'\.com\/(.*?)\/rss', user.rss_url).group(1)
    new_user = User(user.discord_id, user.discord_name, letterboxd_username, latest_id=user.latest_id)
    print("Got user {} with letterboxd username {} and latest_id {}".format(new_user.discord_name, new_user.letterboxd_user, new_user.latest_id))
    new_user.save()
    add_user_to_channel(new_user.discord_id, user.channel_id)
    print("saved user {} to channel id {}".format(new_user.discord_name, user.channel_id))