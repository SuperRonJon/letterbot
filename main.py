import asyncio
import discord
import feedparser
import os
import pickle
import re
import threading
from discord.ext import tasks
from secret import token
from user import User

feed_url = 'https://letterboxd.com/superronjon/rss/'

followed_users = []

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    global followed_users
    print('Logged in as {}'.format(client.user))
    if os.path.exists('./followed.pkl'):
        with open('followed.pkl', 'rb') as f:
            followed_users = pickle.load(f)
        print('Found saved followed users: ')
        for user in followed_users:
            print(user.discord_name)
    else:
        print("No saved followed users")
    client.loop.create_task(update_check_periodically())


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$latest_film'):
        latest = get_latest_entry(feed_url)
        await message.channel.send(embed=build_embed(latest, "SuperRonJon"))
    
    if message.content.startswith('$follow'):
        args = message.content.split(' ')
        if len(args) == 3 and len(message.mentions) == 1:
            if follow_user(message.mentions[0], args[2], message.channel):
                print("Followed {} with letterboxd username {}".format(message.mentions[0].name, args[2]))
                await message.channel.send("Followed {} with letterboxd username {}".format(message.mentions[0].name, args[2]))
            else:
                await message.channel.send("Already following user {}".format(message.mentions[0].name))
        else:
            await message.channel.send("Inavlid command")
    
    if message.content.startswith('$update'):
        await run_update_check()


def follow_user(user, letterboxd_username, disc_channel):
    if already_following_user(user):
        return False
    url = "https://letterboxd.com/{}/rss/".format(letterboxd_username)
    latest_id = 0
    try:
        latest_id = get_latest_entry(url).id
    except: 
        print("couldn't find latest for {}".format(letterboxd_username))

    new_user = User(user, url, latest_id, disc_channel)
    followed_users.append(new_user)

    with open('followed.pkl', 'wb') as f:
        pickle.dump(followed_users, f)

    return True

def get_latest_entry(url):
    feed = feedparser.parse(url)
    return feed.entries[0]

def get_entry_string(entry, username):
    desc = re.search(r'<p>.*?<\/p>.*?<p>(.*?)<\/p>', entry.summary)
    description = desc.group(1)
    return "{} - {}".format(username, description)

def build_embed(entry, username):
    embeded = discord.Embed(title=entry.title, description=get_entry_string(entry, username), color=0x00ff00, type='rich', url=entry.link)
    thumbnail = re.search(r'\"(.*?)\"', entry.summary)
    embeded.set_thumbnail(url=thumbnail.group(1))
    return embeded

def already_following_user(new_user):
    for user in followed_users:
        if user.discord_id == new_user.id:
            return True
    return False

async def run_update_check():
    for user in followed_users:
        latest_id = 0
        try:
            latest_id = get_latest_entry(user.rss_url).id
        except:
            print("Couldn't update username {}".format(user.discord_name))
        
        if latest_id != user.latest_id:
            latest = get_latest_entry(user.rss_url)
            user.latest_id = latest.id
            user_channel = client.get_channel(user.channel_id)
            await user_channel.send(embed=build_embed(latest, user.discord_name))
    
async def update_check_periodically():
    while True:
        await run_update_check()
        await asyncio.sleep(5)


client.run(token)
