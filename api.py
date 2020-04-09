import config, db, roles, crypto
from quart import Quart

def run_api(bot):
    app = Quart(__name__)

    @app.route("/update/<username>")
    async def update(username):
        if (user := db.lookup_by_cryptohack_username(username)) is not None:
            await roles.update_roles(bot, user.discord_id, crypto.get_userscore(username))
            return username + " updated"
        return "Not found"

    bot.loop.create_task(app.run_task())
