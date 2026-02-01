import asyncio
import discord
import os
import random
import json
import letterbot.embeds as embeds
import letterbot.tmdb as tmdb
from letterbot.user_management import follow_user, unfollow_user, already_following_user, get_user_from_row, get_users_cursor, get_all_users_in_channel, get_user_by_discord_id, unfollow_user_by_letterboxd
from letterbot.watched.watch_entry import WatchEntry

try:
    secret_token = os.environ['TOKEN']
except KeyError:
    from secret import token
    secret_token = token

emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
SLEEP_SECONDS = 30


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
                await message.channel.send("Unable to find latest film for {}".format(message.author.name))
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
    
    if message.content.startswith('$letterboxd_unfollow'):
        args = message.content.split(' ')
        if len(args) == 2:
            if(unfollow_user_by_letterboxd(args[1])):
                await message.channel.send("Unfollowed letterboxd user {}.".format(args[1]))
            else:
                await message.channel.send("Failed to unfollow {}. They may not be followed".format(args[1]))
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
    
    if message.content.startswith("$random_poll"):
        args = message.content.split(' ')
        if len(args) <= 1:
            await message.channel.send("Must specify number of options from 1-10 e.g `$random_poll 4`")
        if len(args) > 2:
            await message.channel.send("Too many paramenters, only need one value for number of options.")
        else:
            num_choices = -1
            try:
                num_choices = int(args[1])
            except ValueError:
                await message.channel.send("Invalid number of options.")
            if 1 <= num_choices and num_choices <= 10:
                random_ids = get_random_movies(num_choices)
                if random_ids is not None:
                    results_info = []
                    for id in random_ids:
                        results_info.append(tmdb.get_info_from_id(id))
                    embs = embeds.build_poll_embeds(results_info)
                    sent = await message.channel.send(embeds=embs)
                    for x, id in enumerate(random_ids):
                        await sent.add_reaction(emojis[x])
            else:
                await message.channel.send("Number of options must be between 1-10")
    
    if message.content.startswith("$users_here"):
        users_string = get_users_string(message.channel.id)
        await message.channel.send(users_string)
    
    if message.content.startswith("$film_info"):
        args = message.content.split(' ')
        if len(args) == 1:
            await message.channel.send("invalid query")
        else:
            query = ""
            for arg in args:
                if arg != "$film_info":
                    query += arg + " "
            info = tmdb.get_info_for_search(query)
            try:
                emb = embeds.build_info_embed(info)
                await message.channel.send(embed=emb)
            except:
                await message.channel.send("Error with search")

    if message.content.startswith("$create_poll"):
        args = message.content.split(' ')
        if len(args) == 1:
            await message.channel.send("invalid query")
        else:
            ids = []
            for arg in args:
                if arg != "$create_poll":
                    ids.append(arg)
            results_info = []
            for id in ids:
                results_info.append(tmdb.get_info_from_id(id))
            embs = embeds.build_poll_embeds(results_info)
            sent = await message.channel.send(embeds=embs)
            for x, id in enumerate(ids):
                await sent.add_reaction(emojis[x])
    
    if message.content.startswith("$top_watched"):
        args = message.content.split(' ')
        if len(args) == 1:
            strings = get_watched_strings(*get_user_by_discord_id(message.author.id).get_top_watched())
            await message.channel.send('\n'.join(strings))
        elif len(args) == 2 and len(message.mentions) == 1:
            strings = get_watched_strings(*get_user_by_discord_id(message.mentions[0].id).get_top_watched())
            await message.channel.send('\n'.join(strings))
        elif len(args) == 2:
            try:
                amount = int(args[1])
            except Exception:
                await message.channel.send('Error processing command.')
                return
            strings = get_watched_strings(*get_user_by_discord_id(message.author.id).get_top_watched(amount=amount))
            await message.channel.send('\n'.join(strings))
        elif len(args) == 3 and len(message.mentions) == 1:
            try:
                amount = int(args[2])
            except Exception:
                await message.channel.send('Error processing command.')
                return
            strings = get_watched_strings(*get_user_by_discord_id(message.mentions[0].id).get_top_watched(amount=amount))
            await message.channel.send('\n'.join(strings))
        else:
            await message.channel.send("Invalid parameters")

    if message.content.startswith("$recently_watched"):
        args = message.content.split(' ')
        if len(args) == 1:
            strings = get_watched_strings(*get_user_by_discord_id(message.author.id).get_recently_watched())
            await message.channel.send('\n'.join(strings))
        elif len(args) == 2 and len(message.mentions) == 1:
            strings = get_watched_strings(*get_user_by_discord_id(message.mentions[0].id).get_recently_watched())
            await message.channel.send('\n'.join(strings))
        elif len(args) == 2:
            try:
                amount = int(args[1])
            except Exception:
                await message.channel.send('Error processing command.')
                return
            strings = get_watched_strings(*get_user_by_discord_id(message.author.id).get_recently_watched(amount=amount))
            await message.channel.send('\n'.join(strings))
        elif len(args) == 3 and len(message.mentions) == 1:
            try:
                amount = int(args[2])
            except Exception:
                await message.channel.send('Error processing command.')
                return
            strings = get_watched_strings(*get_user_by_discord_id(message.mentions[0].id).get_recently_watched(amount=amount))
            await message.channel.send('\n'.join(strings))
        else:
            await message.channel.send("Invalid parameters")
        

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
            result += "Discord: " + user.discord_name + " - Letterboxd: " + user.letterboxd_user + "\n"
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
        result.append(random_movie["TMDB ID"])
    return result

def get_watched_strings(names, ratings):
    result = []
    for index, name in enumerate(names):
        if ratings[index] == -1.0:
            rating_string = "X"
        else:
            rating_string = str(ratings[index])
        result.append("{} - {}/5.0".format(name, rating_string))
    return result


async def run_update_check():
    cur = get_users_cursor()
    for row in cur:
        cur_user = get_user_from_row(row)
        actual_latest_entry = None
        actual_latest_id = 0
        try:
            actual_latest_entry = cur_user.get_latest_entry()
        except:
            print("Error pulling latest entry for discord: {} letterboxd: {}".format(cur_user.discord_name, cur_user.letterboxd_user), flush=True)
        if actual_latest_entry is not None:
            actual_latest_id = actual_latest_entry.id
        if actual_latest_id != cur_user.latest_id and actual_latest_id != 0:
            print("Update for {}".format(cur_user.discord_name), flush=True)
            cur_user.update_latest_id(actual_latest_id)
            new_entry = WatchEntry.from_feed(cur_user.discord_id, actual_latest_entry)
            if not cur_user.already_had_entry(new_entry.watch_id):
                new_entry.save()
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
            
        await asyncio.sleep(SLEEP_SECONDS)


client.run(secret_token)
