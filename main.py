import feedparser
import discord
from secret import token

feed_url = 'https://letterboxd.com/superronjon/rss/'
intents = discord.Intents.default()
intents.message_content = True

followed_users = {}

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
        await message.channel.send(get_entry_string(latest, "SuperRonJon"))



def get_latest_entry(url):
    feed = feedparser.parse(url)
    return feed.entries[0]

def get_entry_string(entry, username):
    return "{} watched {} ({}) - {}/5".format(username, entry.letterboxd_filmtitle, entry.letterboxd_filmyear, entry.letterboxd_memberrating)


#latest = get_latest_entry(feed_url)
#print_entry(latest, "SuperRonJon")

client.run(token)