import discord
from discord.ext import commands
import random
import json

class Polls(commands.Cog):
    
    def __init__(self, client):    
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Module: Polls")

    @commands.Cog.listener()
    async def on_message(self, message):

        print(message.channel.id)
        if(message.channel.id == 962433889081626624):
            await message.add_reaction('\N{THUMBS UP SIGN}')
            await message.add_reaction('\N{THUMBS DOWN SIGN}')

async def setup(client):
    await client.add_cog(Polls(client))
