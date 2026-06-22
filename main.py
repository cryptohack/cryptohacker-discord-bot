import discord
from discord import app_commands
from discord.ext import commands
import crypto, db, config, roles, api, fun, captcha

import typing

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

@bot.event
async def on_ready():
    print(discord.utils.oauth_url(config.discord.client_id, permissions=discord.Permissions(manage_roles=True, manage_messages=True)))


def is_app_command(ctx: commands.Context) -> bool:
    return ctx.message.type == discord.MessageType.chat_input_command

async def react(ctx: commands.Context, emoji: str):
    if is_app_command(ctx):
        await ctx.send(emoji, ephemeral=True)
    else:
        await ctx.message.add_reaction(emoji)


@bot.hybrid_command()
@app_commands.default_permissions(use_application_commands=True)
async def connect(ctx, token: str):
    """
        Connect your discord and CryptoHack accounts for progress roles and information finding.

        :param token: The connection token, see <https://cryptohack.org/user/>
    """
    if is_app_command(ctx) or isinstance(ctx.channel, discord.DMChannel):
        await ctx.defer(ephemeral=True)
        try:
            username = crypto.verify_token(token)
            now_disconnected = db.register(username, ctx.author.id)
            for id in now_disconnected:
                await roles.clear_roles(ctx.bot, id)
            await ctx.send(f"You have successfully registered as user {username}.", ephemeral=True)
            score = crypto.get_userscore(username)
            await roles.update_roles(ctx.bot, ctx.author.id, score)
        except Exception as e:
            await ctx.send(f"Something went wrong: {e}", ephemeral=True)
    else:
        await ctx.send("Please register with me in DM, so that people don't steal your glory.")
        await ctx.message.delete()

@bot.hybrid_command()
@app_commands.default_permissions(use_application_commands=True)
async def disconnect(ctx):
    """Unlink your discord and CryptoHack accounts."""
    await ctx.defer(ephemeral=True)
    db.disconnect_by_discord_id(ctx.author.id)
    await roles.clear_roles(ctx.bot, ctx.author.id)
    await react(ctx, "👌")

@bot.hybrid_command()
@app_commands.default_permissions(use_application_commands=True)
async def update(ctx, target_user: discord.User):
    """Update the progress roles for a discord user"""
    if (user := db.lookup_by_discord_id(target_user.id)) is not None:
        await ctx.defer(ephemeral=True)
        score = crypto.get_userscore(user.cryptohack_name)
        await roles.update_roles(ctx.bot, user.discord_id, score)
        await react(ctx, "👌")
    else:
        await ctx.send("I don't know who that is on cryptohack. Registration happens by going to your profile settings and DMing me your token. <https://cryptohack.org/user/>", ephemeral=True)

@bot.hybrid_command()
@app_commands.default_permissions(use_application_commands=True, manage_roles=True)
async def clear(ctx, target_user: discord.User):
    """Clear the progress roles for a user. Diagnostic tool."""
    await roles.clear_roles(ctx.bot, target_user.id)
    await react(ctx, "👌")

@bot.hybrid_command()
@app_commands.default_permissions(use_application_commands=True)
async def whois(ctx, target_user: discord.User):
    """Find out how well a discord user is doing on CryptoHack."""
    if (user := db.lookup_by_discord_id(target_user.id)) is not None:
        score = crypto.get_userscore(user.cryptohack_name)
        await ctx.send(embed=discord.Embed(
            title=score.username, url=config.website.user_url.format(score.username), color=0xfeb32b)
                    .add_field(name="Rank", value=f"{score.global_rank} / {score.num_users}", inline=False)
                    .add_field(name="Score", value=f"{score.points} / {score.total_points}", inline=False)
                    .add_field(name="Solves", value=f"{score.challs_solved} / {score.total_challs}", inline=False))
    else:
        await ctx.send("I don't know who that is on cryptohack. Registration happens by going to your profile settings and DMing me your token. <https://cryptohack.org/user/>", ephemeral=True)

@bot.hybrid_command()
@app_commands.default_permissions(use_application_commands=True)
async def fact(ctx):
    """Fun facts about Bruce."""
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

@bot.hybrid_command()
@app_commands.default_permissions(use_application_commands=True)
async def solved(ctx):
    """Mark the channel for a CTF challenge as solved."""
    if getattr(ctx.channel, "category_id", 0) == config.ctf.category:
        if ctx.channel.name in config.ctf.ignore or (config.ctf.prefix and ctx.channel.name.startswith(config.ctf.prefix)) or (config.ctf.suffix and ctx.channel.name.endswith(config.ctf.suffix)):
            # Explicitely ignored or already done
            print("Ignored")
            return
        else:
            name = ctx.channel.name
            await ctx.channel.edit(reason="!solved", name=config.ctf.prefix + name + config.ctf.suffix)
            await ctx.channel.edit(reason="!solved", position=max(c.position for c in ctx.channel.category.channels) + 1)
            await ctx.bot.get_channel(config.ctf.notify_channel).send(f"<@{ctx.author.id}> just solved {name}, nice job! <@&{config.ctf.team}>")
            await react(ctx, "👍")

@bot.event
async def on_member_join(member):
    await member.send("Welcome to the Cryptohack discord.\nTo prevent spam we have implemented a simple fun verification question.\n" + captcha.get_instructions(member.id))

@bot.hybrid_command()
async def verify(ctx, answer: typing.Optional[str] = None):
    """
        Obtain your verification question or answer it.

        :param answer: The answer to your verification question. Leave this blank to get the question itself.
    """
    if answer is None:
        await ctx.send(captcha.get_instructions(ctx.author.id))
    elif captcha.validate_answer(ctx.author.id, answer):
        await ctx.send("That looks correct.\nCome on in!")
        await roles.add_verified_role(ctx.bot, ctx.author.id)
    else:
        await ctx.send("That doesn't look correct.\n" + captcha.get_instructions(ctx.author.id))


async def setup_hook():
    api.run_api(bot)
    print(await bot.tree.sync())
bot.setup_hook = setup_hook


if __name__ == "__main__":
    bot.run(config.discord.token)
