import discord
from discord.ext import commands
import random
import json

class PollsCog(commands.Cog):
    def __init__(self, bot):    
        self.bot = bot
        self.polls_channel_id : int = 962433889081626624
        self.thumbs_up_emoji : str = '\N{THUMBS UP SIGN}'
        self.thumbs_down_emoji : str = '\N{THUMBS DOWN SIGN}'

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Module: Polls")

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        # Creates poll based off thumbs up/down emojis
        if(message.channel.id == self.polls_channel_id):
            await message.add_reaction(self.thumbs_up_emoji)
            await message.add_reaction(self.thumbs_down_emoji)

async def setup(bot) -> None:
    await bot.add_cog(PollsCog(bot))
