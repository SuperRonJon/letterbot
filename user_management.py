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
        print("Followed new user {} with letterboxd username {}".format(new_user.discord_name, letterboxd_username), flush=True)

        return True
    else:
        #if user is followed - check if they are associated with the same channel
        if not user_in_channel(user.id, disc_channel.id):
            add_user_to_channel(user.id, disc_channel.id)
            print("Followed existing user {} in new channel".format(user.name), flush=True)
            return True
        else:
            print("Already following user {}".format(user.name), flush=True)
            return False

def unfollow_user(user, disc_channel=None):
    if not already_following_user(user.id):
        return False
    if disc_channel is not None:
        print("removing user {} from channel...".format(user.name), flush=True)
        remove_user_from_channel(user.id, disc_channel.id)
        return True
    else:
        print("completely deleted user {}".format(user.name), flush=True)
        delete_user(user.id)
        return True


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


"""
Removes a user completely from the database
Deletes all entries in channel table and user table

@param user_id: discord id of the user to delete
"""
def delete_user(user_id):
    conn = Connection()
    cur = conn.get_cursor()
    cur.execute("DELETE FROM channel WHERE discord_id=?", (user_id,))
    cur.execute("DELETE FROM user WHERE discord_id=?", (user_id,))
    conn.commit()


"""
Removes a user from a broadcast channel
deletes the appropraite frow from the channel table
if the user is no longer a part of any channels, they will be
removed from the user table as well.

@param user_id: discord id of the user to remove
@param channel_id: channel to remove them from
"""
def remove_user_from_channel(user_id, channel_id):
    conn = Connection()
    cur = conn.get_cursor()
    cur.execute("DELETE FROM channel WHERE discord_id=? AND channel_id=?", (user_id, channel_id))
    conn.commit()
    cur.execute("SELECT * FROM channel WHERE discord_id=?", (user_id,))
    results = cur.fetchall()
    if len(results) == 0:
        print("User was removed from final channel, deleting user", flush=True)
        cur.execute("DELETE FROM user WHERE discord_id=?", (user_id,))
        conn.commit()
    else:
        print("User is still in at least one channel, keeping in database", flush=True)
    cur.close()
    


def get_user_by_discord_id(discord_id):
    conn = Connection()
    cur = conn.get_cursor()
    cur.execute("SELECT * FROM user WHERE discord_id=?", (discord_id,))
    results = cur.fetchone()
    cur.close()
    if results is not None:
        return get_user_from_row(results)
    else:
        return None
    

def get_user_from_row(row_data):
    return User(row_data[0], row_data[1], row_data[2], row_data[3])

def get_users_cursor():
    conn = Connection()
    cur = conn.get_cursor()
    cur.execute("SELECT * FROM user")
    return cur

