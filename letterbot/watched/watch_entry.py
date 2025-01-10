from letterbot.connection import Connection

class WatchEntry:

    def __init__(self, discord_id, watch_id, film_title, film_year, tmdb_id, watch_date, rating=-1.0, rewatch=False):
        self.discord_id = discord_id
        self.watch_id = watch_id
        self.film_title = film_title
        self.film_year = film_year
        self.tmdb_id = tmdb_id
        self.watch_date = watch_date
        self.rating = float(rating)
        self.rewatch = rewatch
    
    def save(self):
        data = (self.discord_id, self.watch_id, self.film_title, self.film_year, self.tmdb_id, self.watch_date, self.rating, self.rewatch)
        conn = Connection()
        cur = conn.get_cursor()
        cur.execute("INSERT INTO watched VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
        conn.commit()
        cur.close()
    
    @classmethod
    def from_feed(cls, discord_id, feed_entry):
        rating = -1.0
        if 'letterboxd_memberrating' in feed_entry.keys():
            rating = float(feed_entry.letterboxd_memberrating)
        rewatch = False
        if feed_entry.letterboxd_rewatch == 'Yes':
            rewatch = True
        return cls(discord_id, feed_entry.id, feed_entry.letterboxd_filmtitle, feed_entry.letterboxd_filmyear, feed_entry.tmdb_movieid, feed_entry.letterboxd_watcheddate, rating, rewatch)