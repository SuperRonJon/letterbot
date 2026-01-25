from letterbot.connection import Connection
from letterbot.user import User

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
        new_user.fill_watched_history()
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


"""
Unfollows a user from a given discord channel. 
-If no channel parameter is given the user is completely removed 
from the user table and all channel entries for that user are also removed. 

- If a channel parameter is given the user is removed from that channel only.
If that is the last channel the user is a part of and they have no remaining channels
after deletion, that user is removed from the user tabel and unfollowed completely.

@param user: discord.py user class of the user to unfollow
@param disc_channel: discord.py channel of the channel to unfollow the user in
                     if no channel given they are removed entirely
"""
def unfollow_user(disc_user, disc_channel=None):
    if not already_following_user(disc_user.id):
        print("Unable to unfollow user {} because they are not followed at all".format(disc_user.name), flush=True)
        return False
    if disc_channel is not None:
        user = get_user_by_discord_id(disc_user.id)
        if user.remove_from_channel(disc_channel.id):
            print("removed user {} from channel".format(user.discord_name), flush=True)
            user_channels = user.get_channel_ids()
            if len(user_channels) == 0:
                print("User {} was removed from final channel, deleting user".format(user.discord_name), flush=True)
                delete_user(user.discord_id)
            return True
        else:
            print("Unable to remove user {} from channel. They may not be in it..?".format(user.discord_name), flush=True)
            return False
    else:
        print("completely deleting user {}".format(disc_user.name), flush=True)
        delete_user(disc_user.id)
        return True
    

"""
Unfollows a user completely by letterboxd username

@param letterboxd_username: string of the letterboxd username to unfollow
@return true if user was found and unfollowed, false if user was not able to be found
"""
def unfollow_user_by_letterboxd(letterboxd_username):
    user = get_user_by_letterboxd_username(letterboxd_username)
    if user is None:
        print("Unable to unfollow letterboxd user {} because they are not found.", flush=True)
    if not already_following_user(user.discord_id):
        print("Unable to unfollow letterboxd user {} because they are not followed".format(user.letterboxd_user), flush=True)
        return False
    print("Deleting letterboxd user {}".format(user.letterboxd_user))
    delete_user(user.discord_id)
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
Returns a User class for a specified discord_id from the user table
if the user for the id is not found returns None

@param discord_id: discord_id of the user to retrieve
"""
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
    

"""
Returns a User class for a specified letterboxd_username from the user table
if the user for the letterboxd username is not found returns None

@param letterboxd_username: letterboxd username of the user to retrieve
"""
def get_user_by_letterboxd_username(letterboxd_username):
    conn = Connection()
    cur = conn.get_cursor()
    cur.execute("SELECT * FROM user WHERE letterboxd_user=?", (letterboxd_username,))
    results = cur.fetchone()
    cur.close()
    if results is not None:
        return get_user_from_row(results)
    else:
        return None
    

"""
Returns a user class created from a given database row

@param row_data: the results from a cursor fetch of a SELECT * FROM user query
"""
def get_user_from_row(row_data):
    return User(row_data[0], row_data[1], row_data[2], row_data[3])


"""
Returns a cursor over all users in database
"""
def get_users_cursor():
    conn = Connection()
    cur = conn.get_cursor()
    cur.execute("SELECT * FROM user")
    return cur


def get_all_users_in_channel(channel_id):
    conn = Connection()
    cur = conn.get_cursor()
    discord_ids = []
    users = []
    cur.execute("SELECT discord_id FROM channel WHERE channel_id=?", (channel_id,))
    for row in cur:
        if row[0] not in discord_ids:
            discord_ids.append(row[0])
    for id in discord_ids:
        users.append(get_user_by_discord_id(id)) 
    return users
