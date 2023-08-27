import discord
from discord.ext import commands
import os

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@client.event
async def on_ready():
    print("READY " + str(client.user))


client.run(os.environ["TOKEN"])
