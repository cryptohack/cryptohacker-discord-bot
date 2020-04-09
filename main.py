import discord
from discord.ext import commands
import crypto, db, config, roles

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(discord.utils.oauth_url(config.discord.client_id))

@bot.command()
async def connect(ctx, token : str):
    if isinstance(ctx.channel, discord.DMChannel):
        try:
            username = crypto.verify_token(token)
            db.register(username, ctx.author.id)
            await ctx.send(f"You have successfully registered as user {username}.")
            score = crypto.get_userscore(username)
            await roles.update_roles(ctx, score)
        except Exception as e:
            await ctx.send(f"Something went wrong: {e}")
    else:
        await ctx.send("Please register with me in DM, so that people don't steal your glory.")
        await ctx.message.delete()

@bot.command()
async def update(ctx):
    if (username := db.lookup_by_discord_id(ctx.author.id)) is not None:
        score = crypto.get_userscore(username)
        await roles.update_roles(ctx. score)
    else:
        await ctx.send("I don't know who you are on cryptohack. Please go to your profile settings and DM me your token. <https://cryptohack.org/user/>")

if __name__ == "__main__":
    bot.run(config.discord.token)
