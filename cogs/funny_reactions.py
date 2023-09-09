import discord
from discord.ext import commands
import random
import json
from typing import List

class FunnyReactionsCog(commands.Cog):
    """
    Discord cog that reacts to messages with buzzwords using funny emojis
    """
    def __init__(self, bot):    
        self.bot = bot
        self.buzzwords : List[str] = ['eddie','water','thor','fart','strong','deadlift']
        self.eddieleftarm = '<:eddiearm:794302033523245075>'
        self.eddierightarm = '<:armeddie:794302066201853962>'
        self.eddieshitting = '<:eddieshitting:794198092525338654>'

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Module: FunnyReactions")

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message) -> None:
        # TODO: Do we need to loop through all the different buzzwords if they all have the same response?
        lowercase_content = message.content.lower()
        for word in self.buzzwords:
            if word in lowercase_content:
                await message.add_reaction(self.eddieleftarm)
                await message.add_reaction(self.eddieshitting)
                await message.add_reaction(self.eddierightarm)

async def setup(bot) -> None:
    await bot.add_cog(FunnyReactions(bot))
