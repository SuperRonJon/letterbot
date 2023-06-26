import asyncio
import discord
import os
import random
import json
import letterbot.embeds as embeds
from letterbot.user_management import follow_user, unfollow_user, already_following_user, get_user_from_row, get_users_cursor, get_all_users_in_channel

try:
    secret_token = os.environ['TOKEN']
except KeyError:
    from secret import token
    secret_token = token

emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    client.loop.create_task(update_check_periodically())


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$latest_film'):
        args = message.content.split(' ')
        if len(args) == 2 and len(message.mentions) == 1:
            if not already_following_user(message.mentions[0].id):
                await message.channel.send("Not following user {}".format(message.mentions[0].name))
                return
            emb = embeds.get_latest_film(message.mentions[0].id)
            if emb is not None:
                await message.channel.send(embed=emb)
            else:
                await message.channel.send("Unable to find latest film for {}".format(message.mentions[0].name))
        elif len(args) == 1:
            if not already_following_user(message.author.id):
                await message.channel.send("Not following user {}".format(message.author.name))
                return
            emb = embeds.get_latest_film(message.author.id)
            if emb is not None:
                await message.channel.send(embed=emb)
            else:
                await message.channel.send("Unable to find latest film for {}".format(message.mentions[0].name))
        else:
            await message.channel.send("Invalid command")
            
    
    if message.content.startswith('$follow'):
        args = message.content.split(' ')
        if len(args) == 3 and len(message.mentions) == 1:
            if follow_user(message.mentions[0], args[2], message.channel):
                await message.channel.send("Followed {} with letterboxd username {}".format(message.mentions[0].name, args[2]))
                emb = embeds.get_latest_film(message.mentions[0].id)
                if emb is not None:
                    await message.channel.send(embed=emb)
            else:
                await message.channel.send("Already following user {}".format(message.mentions[0].name))
        else:
            await message.channel.send("Invalid command")
    
    if message.content.startswith('$unfollow'):
        args = message.content.split(' ')
        if len(args) == 2 and len(message.mentions) == 1:
            if unfollow_user(message.mentions[0], message.channel):
                await message.channel.send("Unfollowed {}".format(message.mentions[0]))
            else:
                await message.channel.send("Unable to unfollow {}. They may not be followed in this channel or at all.".format(message.mentions[0]))
        else:
            await message.channel.send("Invalid command")
    
    if message.content.startswith('$update'):
        await run_update_check()
    
    if message.content.startswith('$delete'):
        try:
            async for msg in message.channel.history(limit=100):
                if msg.author == client.user:
                    print("Deleting message: {}".format(msg.content))
                    await msg.delete()
                    return
        except Exception as e:
            print("Error deleting message")
            print(e)
    
    if message.content.startswith("$rand"):
        randoms = get_random_movies(4)
        if randoms is not None:
            emb = embeds.build_movies_embed(randoms)
            sent = await message.channel.send(embed=emb)
            for emoji in emojis:
                await sent.add_reaction(emoji)
    
    if message.content.startswith("$users_here"):
        users_string = get_users_string(message.channel.id)
        await message.channel.send(users_string)
        

def get_all_movies():
    f = open('movies.json')
    return json.load(f)

def get_users_string(channel_id):
    users = get_all_users_in_channel(channel_id)
    result = ""
    if len(users) == 0:
        result = "No users followed in this channel."
    else:
        for user in users:
            result += user.discord_name + "\n"
    return result

def get_random_movies(num):
    result = []
    movies = get_all_movies()
    if len(movies) < num:
        return None
    for i in range(num):
        random_movie = random.choice(movies)
        print(random_movie, flush=True)
        movies.pop(movies.index(random_movie))
        result.append(random_movie)
    return result

async def run_update_check():
    cur = get_users_cursor()
    for row in cur:
        cur_user = get_user_from_row(row)
        actual_latest_entry = cur_user.get_latest_entry()
        actual_latest_id = actual_latest_entry.id
        if actual_latest_id != cur_user.latest_id and actual_latest_id != 0:
            print("Update for {}".format(cur_user.discord_name), flush=True)
            cur_user.update_latest_id(actual_latest_id)
            user_channel_ids = cur_user.get_channel_ids()
            for channel_id in user_channel_ids:
                channel = client.get_channel(channel_id)
                try:
                    to_send = embeds.build_embed(actual_latest_entry, cur_user.discord_name)
                except:
                    print("Error with update for {}".format(cur_user.letterboxd_user), flush=True)
                    to_send = embeds.error_embed(actual_latest_entry, cur_user.discord_name)
                await channel.send(embed=to_send)

async def update_check_periodically():
    while True:
        try:
            await run_update_check()
        except:
            print("Error updating...", flush=True)
            
        await asyncio.sleep(5)


client.run(secret_token)
