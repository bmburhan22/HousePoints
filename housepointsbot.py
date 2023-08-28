servers_path = "./added_servers/"

import discord
from discord.ext import commands
import os, json, copy
from dotenv import load_dotenv
load_dotenv()

def db_open(guild_id, rw):
    os.makedirs(os.path.dirname(servers_path), exist_ok=True)
    return open(f"{servers_path}{guild_id}.json", rw, encoding="utf-8")

def write(guild_id, d):
    db = read(guild_id)
    db.update(d)
    json.dump(db, db_open(guild_id, "w"))

def read(guild_id):
    try:
        return json.load(db_open(guild_id, "r"))
    except:
        return {"points_limit": 50, "houses": {}, "mods": {}}

client = commands.Bot(
    help_command=None,
    command_prefix=commands.when_mentioned_or("/"),
    intents=discord.Intents.all(),
)


@client.event
async def on_ready():
    print(f"{client.user} bot ready!")


@client.command()
async def help(ctx):
    help_message = (
        "Here are the available commands:\n\n"
        + "/points_limit <limit>: Set the points limit.\n"
        + "/houses: Display information about houses and their points.\n"
        + "/user: Display points and house for mentioned users.\n"
        + "/leaderboard: Display a leaderboard of houses and their members' points.\n"
        + "/register: Register a new house.\n"
        + "/delete: Delete a house.\n"
        + "/points <amount> to <user/house>: Add points to users or house.\n"
        + "/points <amount> from <user/house>: Remove points from users or house."
    )
    await ctx.message.reply(help_message)


@client.command()
@commands.has_permissions(administrator=True)
async def points_limit(ctx, limit):
    write(ctx.guild.id, {"points_limit": limit})
    await ctx.message.reply(f'New limit: {read(ctx.guild.id)["points_limit"]}')


@client.command()
async def houses(ctx):
    houses_list = []
    for role_id, members in sorted(
        read(ctx.guild.id)["houses"].items(),
        key=lambda x: sum(x[1].values()),
        reverse=True,
    ):
        total = 0
        house_name = discord.utils.get(ctx.guild.roles, id=int(role_id)).name
        discord.utils.get(ctx.guild.roles, id=int(role_id)).name
        for m, p in members.items():
            total += p
        houses_list.append("House:\t" + house_name + "\t\tTotal Points:\t" + str(total))

    await ctx.message.reply("Houses:\n\n" + "\n\n".join(houses_list))


@client.command()
async def user(ctx):
    h = read(ctx.guild.id)["houses"]
    user_list = []
    for role_id, members in h.items():
        for m, p in members.items():
            if m in [
                str(member.id)
                for member in ctx.message.mentions
                if member != client.user
            ]:
                user_list.append(
                    client.get_user(int(m)).name
                    + "\t\tPoints:\t"
                    + str(p)
                    + "\t\t"
                    + "House:\t"
                    + discord.utils.get(ctx.guild.roles, id=int(role_id)).name
                )

    await ctx.message.reply("Users:\n\n" + "\n\n".join(user_list))


@client.command()
async def leaderboard(ctx):
    houses_list = []
    for role_id, members in sorted(
        read(ctx.guild.id)["houses"].items(),
        key=lambda x: sum(x[1].values()),
        reverse=True,
    ):
        total = 0
        house_name = discord.utils.get(ctx.guild.roles, id=int(role_id)).name
        discord.utils.get(ctx.guild.roles, id=int(role_id)).name
        member_names = []

        for m, p in sorted(members.items(), key=lambda x: x[1], reverse=True)[:5]:
            member_names.append(f"{client.get_user(int(m)).name}\t\tPoints:\t{p}")
            total += p
        houses_list.append(
            "House:\t"
            + house_name
            + "\t\tTotal Points:\t"
            + str(total)
            + "\nMembers:\n"
            + "\n".join(member_names)
        )

    await ctx.message.reply("Leaderboard:\n\n" + "\n\n".join(houses_list))


@client.event
async def on_member_update(before, after):
    await sync_guild(before.guild)
    # if before.roles != after.roles:
    #     roles_removed = set(before.roles) - set(after.roles)
    #     roles_added = set(after.roles) - set(before.roles)
    #     db = read(before.guild.id)

    #     for role in roles_removed:
    #         role_id = str(role.id)
    #         if role_id in db["houses"]:
    #             del db["houses"][role_id][str(after.id)]

    #     for role in roles_added:
    #         role_id = str(role.id)
    #         if role_id in db["houses"]:
    #             db["houses"][role_id][str(after.id)] = 0

    #     write(ctx.guild.id, db)


@client.command()
@commands.has_permissions(administrator=True)
async def register(ctx):
    db = read(ctx.guild.id)
    for role in ctx.message.role_mentions:
        role_id = str(role.id)
        if role_id not in db["houses"]:
            db["houses"][role_id] = {}

    write(ctx.guild.id, db)
    await houses(ctx)


@client.command()
@commands.has_permissions(administrator=True)
async def delete(ctx):
    db = read(ctx.guild.id)
    for role in ctx.message.role_mentions:
        del db["houses"][str(role.id)]

    write(ctx.guild.id, db)
    await houses(ctx)


@client.command()
async def points(ctx, p, tofrom):
    if not any(
        str(r.id) in [m for m in read(ctx.guild.id)["mods"]] for r in ctx.author.roles
    ):
        return
    p = int(p)
    db = read(ctx.guild.id)
    if tofrom.lower() == "to":
        t = 0
    elif tofrom.lower() == "from":
        t = 1
    else:
        t = -1

    limit = int(db["points_limit"])

    if p > limit:
        await ctx.message.reply(
            f'Exceeded points limit of {read(ctx.guild.id)["points_limit"]}'
        )
    else:
        if t < 0:
            await ctx.message.reply(f"Error in command")
        else:
            points_change = {}
            for member in ctx.message.mentions:
                member_id = str(member.id)
                role_id = ""
                for h, members in db["houses"].items():
                    if member_id in members.keys():
                        role_id = h
                if not role_id:
                    continue

                if member_id not in db["houses"][role_id]:
                    db["houses"][role_id][member_id] = 0
                if t == 0:
                    db["houses"][role_id][member_id] += p
                elif t == 1:
                    if db["houses"][role_id][member_id] > p:
                        db["houses"][role_id][member_id] -= p
                    else:
                        db["houses"][role_id][member_id] = 0
                points_change[member_id] = db["houses"][role_id][member_id]

            for role in ctx.message.role_mentions:
                role_id = str(role.id)
                for member_id in db["houses"][role_id].keys():
                    if t == 0:
                        db["houses"][role_id][member_id] += p
                    elif t == 1:
                        if db["houses"][role_id][member_id] > p:
                            db["houses"][role_id][member_id] -= p
                        else:
                            db["houses"][role_id][member_id] = 0
                    points_change[member_id] = db["houses"][role_id][member_id]
            write(ctx.guild.id, db)
            await ctx.message.reply(
                "\n".join(
                    [f"User:<@{m}>\t\tPoints:{p}" for m, p in points_change.items()]
                )
            )


@client.command()
@commands.has_permissions(administrator=True)
async def mod(ctx, addremove):
    db = read(ctx.guild.id)
    print(db)
    for role in ctx.message.role_mentions:
        role_id = str(role.id)
        if role_id not in db["mods"]:
            if addremove == "add":
                db["mods"][role_id] = 0
        else:
            if addremove == "remove":
                del db["mods"][role_id]

    write(ctx.guild.id, db)
    await ctx.message.reply(
        f'Mods: {", ".join ([ discord.utils.get(ctx.guild.roles, id=int(mod)).name  for mod in read(ctx.guild.id)["mods"]])}'
    )


async def sync_guild(guild):
    db = read(guild.id)
    copy_db = copy.deepcopy(db)
    for house_id in copy_db["houses"].keys():
        guild_roles = [str(r.id) for r in guild.roles]
        if house_id not in guild_roles:
            del db["houses"][house_id]
        else:
            guild_members = [
                str(m.id)
                for m in discord.utils.get(guild.roles, id=int(house_id)).members
            ]
            for m_id in guild_members:
                if m_id not in db["houses"][house_id].keys():
                    db["houses"][house_id][m_id] = 0
            for m_id in copy_db["houses"][house_id].keys():
                if m_id not in guild_members:
                    del db["houses"][house_id][m_id]

    write(guild.id, db)


@client.command()
async def sync(ctx):
    await sync_guild(ctx.guild)


client.run(os.environ["TOKEN"])
