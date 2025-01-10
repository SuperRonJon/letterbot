import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from letterbot.connection import Connection
import letterbot.user_management as Users


con = Connection()
cur = con.get_cursor()
cur.execute("CREATE TABLE watched(discord_id, watch_id, film_title, film_year, tmdb_id, watch_date, rating, rewatch)")

users = Users.get_users_cursor()
for row in users:
    user = Users.get_user_from_row(row)
    user.fill_watched_history()
