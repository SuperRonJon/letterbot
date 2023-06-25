from connection import Connection
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
    
    def get_latest_entry(self):
        feed = feedparser.parse(self.rss_url)
        return feed.entries[0]

    def get_latest_id(self):
        try:
            latest = self.get_latest_entry()
            return latest.id
        except:
            print("couldn't get latest id for {}".format(self.letterboxd_user))
            return 0
