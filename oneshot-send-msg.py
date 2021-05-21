import discord, config

intents = discord.Intents.default()
intents.members = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    text_channel_list = []
    guild = bot.get_guild(config.user_verification.guild_id)
    for channel in guild.text_channels:
        text_channel_list.append(channel)
    print(text_channel_list)
    msg = """Welcome to the CryptoHack Discord chat server!

To ensure our users aren't bothered by Discord spam, we need you to pass a quick captcha.

Our resident CryptoHacker bot has privately messaged you, after you successfully complete the verification, you will have access to the chat.

<:ch:692807409084923945>
"""
    bla = await bot.fetch_channel(816074538231660664)
    #await bla.send(msg)

if __name__ == "__main__":
    bot.run(config.discord.token)

