import discord, config

intents = discord.Intents.default()
intents.members = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    guild = bot.get_guild(config.user_verification.guild_id)
    role = [r for r in await guild.fetch_roles() if r.name == config.user_verification.role][0]
    async for member in guild.fetch_members(limit=None):
        #await(member.add_roles(role))
        print(member)

if __name__ == "__main__":
    bot.run(config.discord.token)

