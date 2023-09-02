import discord
from discord.ext import commands
import random
import json

class FunnyReactions(commands.Cog):
    
    def __init__(self, client):    
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Module: FunnyReactions")

    @commands.Cog.listener()
    async def on_message(self, message):
        buzzwords = ['eddie','water','thor','fart','strong','deadlift']
        for word in buzzwords:
            if word in message.content.lower():
                await message.add_reaction('<:eddiearm:794302033523245075>')
                await message.add_reaction('<:eddieshitting:794198092525338654>')
                await message.add_reaction('<:armeddie:794302066201853962>')

async def setup(client):
    await client.add_cog(FunnyReactions(client))
