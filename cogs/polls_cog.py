import discord
from discord.ext import commands
import random
import json
from typing import Final, Dict

class PollsCog(commands.Cog):
    POLLS_CHANNEL_ID : Final[int] = 962433889081626624
    EMOJIS : Final[Dict[str,str]] = {
        "thumbs_up": '\N{THUMBS UP SIGN}',
        "thumbs_down": '\N{THUMBS DOWN SIGN}'
    }

    def __init__(self, bot):    
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Module: Polls")

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        # Creates poll based off thumbs up/down emojis
        if(message.channel.id == PollsCog.POLLS_CHANNEL_ID):
            await message.add_reaction(PollsCog.EMOJIS["thumbs_up"])
            await message.add_reaction(PollsCog.EMOJIS["thumbs_down"])

async def setup(bot) -> None:
    await bot.add_cog(PollsCog(bot))
