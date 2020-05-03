import discord
from discord.ext import commands
import crypto, db, config, roles, api, fun

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(discord.utils.oauth_url(config.discord.client_id))

@bot.command()
async def connect(ctx, token : str):
    if isinstance(ctx.channel, discord.DMChannel):
        try:
            username = crypto.verify_token(token)
            now_disconnected = db.register(username, ctx.author.id)
            for id in now_disconnected:
                await roles.clear_roles(ctx.bot, id)
            await ctx.send(f"You have successfully registered as user {username}.")
            score = crypto.get_userscore(username)
            await roles.update_roles(ctx.bot, ctx.author.id, score)
        except Exception as e:
            await ctx.send(f"Something went wrong: {e}")
    else:
        await ctx.send("Please register with me in DM, so that people don't steal your glory.")
        await ctx.message.delete()

@bot.command()
async def disconnect(ctx):
    db.disconnect_by_discord_id(ctx.author.id)
    await roles.clear_roles(ctx.bot, ctx.author.id)
    await ctx.message.add_reaction("👌")

@bot.command()
async def update(ctx, target_user : discord.User):
    if (user := db.lookup_by_discord_id(target_user.id)) is not None:
        score = crypto.get_userscore(user.cryptohack_name)
        await roles.update_roles(ctx.bot, user.discord_id, score)
        await ctx.message.add_reaction("👌")
    else:
        await ctx.send("I don't know who that is on cryptohack. Registration happens by going to your profile settings and DMing me your token. <https://cryptohack.org/user/>")

@bot.command()
async def clear(ctx, target_user : discord.User):
    await roles.clear_roles(ctx.bot, target_user.id)
    await ctx.message.add_reaction("👌")

@bot.command()
async def whois(ctx, target_user : discord.User):
    if (user := db.lookup_by_discord_id(target_user.id)) is not None:
        score = crypto.get_userscore(user.cryptohack_name)
        await ctx.send(embed=discord.Embed(
            title=score.username, url=config.website.user_url.format(score.username), color=0xfeb32b)
                    .add_field(name="Rank", value=f"{score.global_rank} / {score.num_users}", inline=False)
                    .add_field(name="Score", value=f"{score.points} / {score.total_points}", inline=False)
                    .add_field(name="Solves", value=f"{score.challs_solved} / {score.total_challs}", inline=False))
    else:
        await ctx.send("I don't know who that is on cryptohack. Registration happens by going to your profile settings and DMing me your token. <https://cryptohack.org/user/>")

@bot.command()
async def fact(ctx):
    f = fun.get_bruce_fact()
    await ctx.send(embed=discord.Embed(title="Bruce Schneier Fact", color=0xfeb32b, description=f).set_footer(text="Powered by https://www.schneierfacts.com"))
   

@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    user = await guild.fetch_member(payload.user_id)
    await roles.process_reaction(user.add_roles, payload.message_id, guild, payload.emoji.name)

@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    user = await guild.fetch_member(payload.user_id)
    await roles.process_reaction(user.remove_roles, payload.message_id, guild, payload.emoji.name)

if __name__ == "__main__":
    api.run_api(bot)
    bot.run(config.discord.token)
