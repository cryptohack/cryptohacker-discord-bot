import dataclasses
import requests
import config

class error(Exception): pass

def verify_token(token : str):
    """Verify a token containing the cryptohack username, return the username or None when invalid"""
    response = requests.get(f"{config.api.base}{config.api.usertoken_endpoint}{token}").json()
    if "error" in response:
        raise error(response["error"])
    return response["user"]

@dataclasses.dataclass
class Score:
    username : str
    global_rank : int
    points : int
    total_points : int
    challs_solved : int
    total_challs : int
    num_users : int

    @classmethod
    def parse(cls, raw):
        #username:global_rank:points:total_points:challs_solved:total_challs:num_users
        spl = raw.split(":")
        assert len(spl) == 7
        username = spl.pop(0)
        return cls(*([username] + list(map(int, spl))))

def get_userscore(username):
    response = requests.get(f"{config.api.base}{config.api.userscore_endpoint}", params={"authkey": config.api.authkey, "username": username}).text
    return Score.parse(response)

def fetch_scoreboard(page):
    return requests.get(f"{config.api.base}{config.api.scoreboard_endpoint}".format(page)).json()["rankings"]
