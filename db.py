import config
from pony.orm import *

db = Database()

class User(db.Entity):
    cryptohack_name = Required(str, unique=True)
    discord_id = Required(int, unique=True)

db.bind(**config.db._raw)
db.generate_mapping(create_tables=True)

@db_session
def lookup_by_discord_id(id : int):
    return User.get(discord_id = id)

@db_session
def lookup_by_cryptohack_username(username : str):
    return User.get(cryptohack_name = username)

@db_session
def register(username : str, id : int):
    # TODO: do something when the user is already linked
    User(username, id)
