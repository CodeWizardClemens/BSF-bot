import discord
from discord.ext import commands
from typing import List, Final, Dict

class FunnyReactionsCog(commands.Cog):
    """
    Discord cog that reacts to messages with buzzwords using funny emojis
    """

    BUZZWORDS : Final[List[str]] = ['eddie','water','thor','fart','strong','deadlift']
    REACTIONS : Final[Dict[str, str]] = {
        "eddieleftarm": '<:eddiearm:794302033523245075>',
        "eddierightarm": '<:armeddie:794302066201853962>',
        "eddieshitting": '<:eddieshitting:794198092525338654>'
    }
    def __init__(self, bot):    
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Module: FunnyReactions")

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message) -> None:
        # TODO: Do we need to loop through all the different buzzwords if they all have the same response?
        lowercase_content = message.content.lower()
        for word in FunnyReactionsCog.BUZZWORDS:
            if word in lowercase_content:
                await message.add_reaction(FunnyReactionsCog.REACTIONS["eddieleftarm"])
                await message.add_reaction(FunnyReactionsCog.REACTIONS["eddieshitting"])
                await message.add_reaction(FunnyReactionsCog.REACTIONS["eddierightarm"])

async def setup(bot) -> None:
    await bot.add_cog(FunnyReactionsCog(bot))
