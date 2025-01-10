from letterbot.connection import Connection
from letterbot.watched.watch_entry import WatchEntry

import feedparser

class User:

    def __init__(self, discord_id, discord_name, letterboxd_user, latest_id=None):
        self.discord_name = discord_name
        self.discord_id = discord_id
        self.letterboxd_user = letterboxd_user
        self.rss_url = "https://letterboxd.com/{}/rss/".format(letterboxd_user)
        if latest_id is not None:
            self.latest_id = latest_id
        else:
            self.latest_id = self.get_latest_id()
    
    def save(self):
        data = (self.discord_id, self.discord_name, self.letterboxd_user, self.latest_id)
        connect = Connection()
        cur = connect.get_cursor()
        cur.execute("INSERT INTO user VALUES (?, ?, ?, ?)", data)
        connect.commit()
        cur.close()
    
    def update_latest_id(self, latest_id):
        connect = Connection()
        cur = connect.get_cursor()
        cur.execute("UPDATE user SET latest_id = ? WHERE discord_id = ?", (latest_id, self.discord_id))
        connect.commit()
        cur.close()
        self.latest_id = latest_id
    
    def get_latest_entry(self):
        feed = feedparser.parse(self.rss_url)
        return feed.entries[0]

    def get_latest_id(self):
        try:
            latest = self.get_latest_entry()
            return latest.id
        except:
            print("Couldn't get latest id for {}".format(self.letterboxd_user), flush=True)
            return 0
    
    def get_channel_ids(self):
        conn = Connection()
        cur = conn.get_cursor()
        cur.execute("SELECT channel_id FROM channel WHERE discord_id=?", (self.discord_id,))
        results = cur.fetchall()
        response = []
        for result in results:
            response.append(result[0])
        return response
    
    def remove_from_channel(self, channel_id):
        current_ids = self.get_channel_ids()
        if channel_id in current_ids:
            conn = Connection()
            cur = conn.get_cursor()
            cur.execute("DELETE FROM channel WHERE discord_id=? AND channel_id=?", (self.discord_id, channel_id))
            conn.commit()
            return True
        else:
            return False
    
    def already_had_entry(self, watch_id):
        conn = Connection()
        cur = conn.get_cursor()
        cur.execute("SELECT * FROM watched WHERE discord_id=? AND watch_id=?", (self.discord_id, watch_id))
        results = cur.fetchall()
        cur.close()
        return len(results) > 0
    
    def fill_watched_history(self):
        entries = feedparser.parse(self.rss_url).entries
        for entry in entries:
            try:
                watch_entry = WatchEntry.from_feed(self.discord_id, entry)
            except Exception:
                print("Error with parsing entry for user {}".format(self.discord_name))
                break
            if not self.already_had_entry(watch_entry.watch_id):
                watch_entry.save()
            else:
                print("Already had entry {}".format(watch_entry.film_title))
    
    def get_top_watched(self, amount=10):
        conn = Connection()
        cur = conn.get_cursor()
        cur.execute("SELECT * FROM watched WHERE discord_id=? GROUP BY tmdb_id ORDER BY rating DESC", (self.discord_id,))
        results = cur.fetchall()
        cur.close()
        movie_names = []
        movie_ratings = []
        i = 0
        for row in results:
            if i < amount:
                movie_names.append(row[2])
                movie_ratings.append(row[6])
                i += 1
            else:
                break
        return (movie_names, movie_ratings)
    
    def get_recently_watched(self, amount=10):
        conn = Connection()
        cur = conn.get_cursor()
        cur.execute("SELECT * FROM watched WHERE discord_id=? ORDER BY watch_date DESC", (self.discord_id,))
        results = cur.fetchall()
        cur.close()
        movie_names = []
        movie_ratings = []
        i = 0
        for row in results:
            if i < amount:
                movie_names.append(row[2])
                movie_ratings.append(row[6])
                i += 1
            else:
                break
        return (movie_names, movie_ratings)
