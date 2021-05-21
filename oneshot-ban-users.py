import discord, config

intents = discord.Intents.default()
intents.members = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    guild = bot.get_guild(config.user_verification.guild_id)
    for m in guild.members:
        before = m.name.split('#')[0]
        if before.count(' ') == 1 and '2021-05-17' in str(m.joined_at):
            print(f"{m.joined_at} {m.name}")
            input("Proceed to ban?")
            #await m.ban()

if __name__ == "__main__":
    bot.run(config.discord.token)

