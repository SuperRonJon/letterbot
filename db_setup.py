from connection import Connection

con = Connection()
cur = con.get_cursor()

cur.execute("CREATE TABLE user(discord_id, discord_name, letterboxd_user, latest_id)")
cur.execute("CREATE TABLE channel(discord_id, channel_id)")