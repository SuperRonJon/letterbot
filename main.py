import feedparser
import discord
import re
from secret import token
from user import User

feed_url = 'https://letterboxd.com/superronjon/rss/'
intents = discord.Intents.default()
intents.message_content = True

followed_users = []

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('Logged in as {}'.format(client.user))


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
            follow_user(message.mentions[0], args[2], message.channel)
            print("Followed {} with letterboxd username {}".format(message.mentions[0].name, args[2]))
        else:
            await message.channel.send("Inavlid command")
    
    if message.content.startswith('$update'):
        await run_update_check()


def follow_user(user, letterboxd_username, disc_channel):
    url = "https://letterboxd.com/{}/rss/".format(letterboxd_username)
    latest_id = 0
    try:
        latest_id = get_latest_entry(url).id
    except: 
        print("couldn't find latest for {}".format(letterboxd_username))

    new_user = User(user, url, latest_id, disc_channel)
    followed_users.append(new_user)

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

def already_following_user(user):
    for user in followed_users:
        if user.discord == user:
            return True
    return False

async def run_update_check():
    for user in followed_users:
        latest_id = 0
        try:
            latest_id = get_latest_entry(user.rss_url).id
        except:
            print("Couldn't update username {}".format(user.discord.name))
        
        if latest_id != user.latest_id:
            latest = get_latest_entry(user.rss_url)
            user.latest_id = latest.id
            await user.channel.send(embed=build_embed(latest, user.discord.name))
        else:
            print("No update")


client.run(token)