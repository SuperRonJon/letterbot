import sqlite3
from connection import Connection
from user_management import already_following_user, user_in_channel

class FakeUser:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class FakeUser2:
    def __init__(self, id, name):
        self.discord_id = id
        self.name = name

class FakeChannel:
    def __init__(self, id):
        self.id = id

con = Connection()
cur = con.get_cursor()

cur.execute("CREATE TABLE user(discord_id, discord_name, letterboxd_user, latest_id)")
cur.execute("CREATE TABLE channel(discord_id, channel_id)")

data = [
    (20, "SuperRonJon", "superronjon", "letterboxd-review-400778292"),
    (15, "Seute", "steelerskid559", "letterboxd-review-500")
]

users = [
    FakeUser(15, "Seute"),
    FakeUser(21, "Jimothy")
]

channels =[
    (20, 100),
    (21, 101),
    (18, 501),
    (21, 100),
    (17, 100)
]

cur.executemany("INSERT INTO user VALUES(?, ?, ?, ?)", data)
con.commit()
cur.executemany("INSERT INTO channel VALUES (?, ?)", channels)
con.commit()

if already_following_user(users[0].id):
    print("following first")
else:
    print("not following first")

if already_following_user(users[1].id):
    print("following second")
else:
    print("not following second")

if user_in_channel(21, 100):
    print("in first channel")
else:
    print("not in first channel")

if user_in_channel(18, 100):
    print("in second channel")
else:
    print("not in second channel")
    
