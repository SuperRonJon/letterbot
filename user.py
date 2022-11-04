class User:

    def __init__(self, discord_user, rss_url, latest_id, channel):
        self.discord = discord_user
        self.rss_url = rss_url
        self.latest_id = latest_id 
        self.channel = channel