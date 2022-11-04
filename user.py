class User:

    def __init__(self, discord_user, rss_url, latest_id, channel):
        self.discord_name = discord_user.name
        self.discord_id = discord_user.id
        self.rss_url = rss_url
        self.latest_id = latest_id 
        self.channel_id = channel.id