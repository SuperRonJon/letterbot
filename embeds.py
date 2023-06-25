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

def build_movies_embed(movies):
    fields_array = []
    for i, movie in enumerate(movies):
        new_dict = {}
        new_dict["name"] = "{}. {} ({})".format(i+1, movie["Title"], movie["Year"])
        new_dict["value"] = movie["IMDB Link"]
        fields_array.append(new_dict)
    
    embeded = discord.Embed(title="Movie Choices!", description="React with the number for the movie you'd like to watch", color=0x00ffff, type='rich')
    for field in fields_array:
        embeded.add_field(name=field["name"], value=field["value"], inline=False)
    return embeded
    
