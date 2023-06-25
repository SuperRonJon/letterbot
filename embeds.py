import discord
import re
from user_management import already_following_user, get_user_by_discord_id


def get_entry_string(entry, username):
    desc = re.search(r'<p>.*?<\/p>.*?<p>(.*?)<\/p>', entry.summary)
    description = desc.group(1)
    return "{} - {}".format(username, description)

def build_embed(entry, username):
    embeded = discord.Embed(title=entry.title, description=get_entry_string(entry, username), color=0x00ff00, type='rich', url=entry.link)
    thumbnail = re.search(r'\"(.*?)\"', entry.summary)
    embeded.set_thumbnail(url=thumbnail.group(1))
    return embeded

def error_embed(entry, username):
    embeded = discord.Embed(title=entry.title, description=username, color=0xff0000, type='rich', url=entry.link)
    return embeded

"""
Get embed of the most recent film to post for discord user

@param discord_id: discord id of the user to get most recent film for
"""
def get_latest_film(discord_id):
    if not already_following_user(discord_id):
        return None
    
    user = get_user_by_discord_id(discord_id)
    if user is None:
        return None
    
    latest_entry = user.get_latest_entry()
    return build_embed(latest_entry, user.discord_name)
    
