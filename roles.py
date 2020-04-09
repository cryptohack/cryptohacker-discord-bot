import bisect
import config

async def update_roles(ctx, score):
    async def add_role_by_name(name):
        await ctx.author.add_roles([r for r in guild.roles if r.name == name][0])

    guild = ctx.bot.get_guild(config.levels.guild_id)

    # Clean roles:
    for role in guild.roles:
        if role.name in config.levels.names + config.levels.rank_names:
            await ctx.author.remove_roles(role)

    # Find the correct level role
    ptidx = max(0, bisect.bisect_right(config.levels.points, score.total_points) - 1)
    if 0 <= ptidx < len(config.levels.names):
        await add_role_by_name(config.levels.names[ptidx])

    # Find potentially a rank role
    for rank, name in zip(config.levels.ranks, config.levels.rank_names):
        if score.global_rank <= rank:
            await add_role_by_name(name)
            break
