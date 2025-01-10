import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from letterbot.connection import Connection

con = Connection()
cur = con.get_cursor()

cur.execute("CREATE TABLE user(discord_id, discord_name, letterboxd_user, latest_id)")
cur.execute("CREATE TABLE channel(discord_id, channel_id)")
cur.execute("CREATE TABLE watched(discord_id, watch_id, film_title, film_year, tmdb_id, watch_date, rating, rewatch)")