import discord
import crypto, db, config

class Bot(discord.Client):
    async def on_ready(self):
        print("Ready to roll")

    async def on_message(self, message):
        if message.author == self.user: return

        if isinstance(message.channel, discord.DMChannel):
            # I hope this means it's a DM :)
            if (username := crypto.verify_token(message.content)) is not None:
                print(f"Registering discord id {message.author.id} for user {username}")
                db.register(username, message.author.id)
            else:
                await message.channel.send("This seems to be an invalid token, get your token from <todo_insert_site> and send it to me.")

if __name__ == "__main__":
    Bot().run(config.discord.token)
