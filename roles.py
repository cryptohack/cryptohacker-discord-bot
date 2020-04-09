import bisect
import config

async def clear_roles(bot, user_id):
    guild = bot.get_guild(config.levels.guild_id)
    member = guild.get_member(user_id)

    # Clean roles:
    for role in guild.roles:
        if role.name in config.levels.names + config.levels.rank_names and role.name in [r.name for r in member.roles]:
            await member.remove_roles(role)

async def update_roles(bot, user_id, score):
    async def add_role_by_name(name):
        await member.add_roles([r for r in guild.roles if r.name == name][0])

    guild = bot.get_guild(config.levels.guild_id)
    member = guild.get_member(user_id)

    await clear_roles(bot, user_id)

    # Find the correct level role
    ptidx = max(0, bisect.bisect_right(config.levels.points, score.points) - 1)
    if 0 <= ptidx < len(config.levels.names):
        await add_role_by_name(config.levels.names[ptidx])

    # Find potentially a rank role
    for rank, name in zip(config.levels.ranks, config.levels.rank_names):
        if score.global_rank <= rank:
            await add_role_by_name(name)
            break

async def process_reaction(callback, message_id, guild, emoji):
    if (actions := config.role_reactions.get(str(message_id))) is not None:
        for act in actions:
            if act.emoji == emoji:
                await callback([r for r in guild.roles if r.name == act.role][0])
