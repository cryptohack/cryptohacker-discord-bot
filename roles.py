import bisect
import requests
import config, crypto, db
import logging

async def refresh_top_roles(guild):
    collected = []
    i = 1
    while len(collected) < max(config.levels.ranks):
        collected += crypto.fetch_scoreboard(i)
        i += 1

    usermapping = {e["username"]: e["rank"] for e in collected}
    for limit, role_name in zip(config.levels.ranks, config.levels.rank_names):
        role = [r for r in guild.roles if r.name == role_name][0]
        for m in role.members:
            # Remove all old role members that no longer belong
            m_username = db.lookup_by_discord_id(m.id)
            if m_username is None: continue
            m_username = m_username.cryptohack_name

            if m_username in usermapping and usermapping[m_username] <= limit:
                del usermapping[m_username]
            else:
                await m.remove_roles(role)

        for user in [u for u, v in usermapping.items() if v <= limit]:
            # Add this role to all who deserve it
            del usermapping[user]
            if (m_id := db.lookup_by_cryptohack_username(user)) is not None:
                try:
                    member = await guild.fetch_member(m_id.discord_id)
                except:
                    logging.info(f"Member not found for {user}")
                    continue
                await member.add_roles(role)
                

async def clear_roles(bot, user_id):
    """Returns the top x role name that was removed, if any"""
    guild = bot.get_guild(config.levels.guild_id)
    member = await guild.fetch_member(user_id)

    member_roles = [r.name for r in member.roles]

    top_role = None

    # Clean roles:
    for role in guild.roles:
        if role.name in config.levels.names + config.levels.rank_names and role.name in member_roles:
            await member.remove_roles(role)
            if role.name in config.levels.rank_names:
                top_role = role.name

    return top_role

async def update_roles(bot, user_id, score):
    async def add_role_by_name(name):
        logging.info(f"add role by name: {name}")
        await member.add_roles([r for r in guild.roles if r.name == name][0])

    guild = bot.get_guild(config.levels.guild_id)
    member = await guild.fetch_member(user_id)
    logging.info(f"update roles for member {member.name}")


    old_top_role = await clear_roles(bot, user_id)
    logging.info(f"Old_top_role: {old_top_role}")

    # Find the correct level role
    ptidx = max(0, bisect.bisect_right(config.levels.points, score.points) - 1)
    if 0 <= ptidx < len(config.levels.names):
        await add_role_by_name(config.levels.names[ptidx])

    # Find potentially a rank role
    for rank, name in zip(config.levels.ranks, config.levels.rank_names):
        if score.global_rank <= rank:
            logging.info(f"Found a rank role: {name}")
            if name != old_top_role:
                logging.info(f"It's different, updating everything")
                await refresh_top_roles(guild)
            else:
                logging.info(f"It's the old one, just add it back")
                await add_role_by_name(old_top_role)
            break
    else:
        logging.info(f"No rank role found")

async def process_reaction(callback, message_id, guild, emoji):
    if (actions := config.role_reactions.get(str(message_id))) is not None:
        for act in actions:
            if act.emoji == emoji:
                await callback([r for r in guild.roles if r.name == act.role][0])

async def add_verified_role(bot, user_id):
    guild = bot.get_guild(config.user_verification.guild_id)
    member = await(guild.fetch_member(user_id))
    await member.add_roles([r for r in guild.roles if r.name == config.user_verification.role])
