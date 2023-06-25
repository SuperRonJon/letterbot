from connection import Connection
from user import User

"""
Checks if the discord user is already in the user database

@param user_id: discord id of the user to check
"""
def already_following_user(user_id):
    conn = Connection()
    cur = conn.get_cursor()
    cur.execute("SELECT * FROM user WHERE discord_id=?", (user_id,))
    results = cur.fetchall()
    cur.close()
    return len(results) > 0

"""
Checks if the user is already associated with the given discord channel

@param user_id: discord id of the user being checked
@param channel_id: channel id of the channel being checked
"""
def user_in_channel(user_id, channel_id):
    conn = Connection()
    cur = conn.get_cursor()
    cur.execute("SELECT * FROM channel WHERE discord_id=?", (user_id,))
    results = cur.fetchall()
    cur.close()
    for row in results:
        if row[1] == channel_id:
            return True
    
    return False

"""
Creates a new User class object and saves that user 
and their broadcast channel to the database

@param user: discord.py user class object
@param letterboxd_username: string - the letterboxd username 
                            to associate with that user
@param disc_channel: discord.py channel class object to broadcast user to
"""
def follow_user(user, letterboxd_username, disc_channel):
    if not already_following_user(user.id):
        new_user = User(user.id, user.name, letterboxd_username)
        new_user.save()
        add_user_to_channel(new_user.discord_id, disc_channel.id)

        return True
    else:
        #if user is followed - check if they are associated with the same channel
        if not user_in_channel(user.id, disc_channel.id):
            add_user_to_channel(user.id, disc_channel.id)
            return True
        else:
            return False

"""
Adds a new broadcast channel for a user

@param user_id: discord id of the user to add
@param channel_id: discord channel id of the channel to add
"""
def add_user_to_channel(user_id, channel_id):
    data = (user_id, channel_id)
    conn = Connection()
    cur = conn.get_cursor()
    cur.execute("INSERT INTO channel VALUES(?, ?)", data)
    conn.commit()
    cur.close()


def get_user_by_discord_id(discord_id):
    conn = Connection()
    cur = conn.get_cursor()
    cur.execute("SELECT * FROM user WHERE discord_id=?", (discord_id,))
    results = cur.fetchone()
    cur.close()
    if results is not None:
        return User(results[0], results[1], results[2], results[3])
    else:
        return None
    


