import sys
sys.path.append(("../../fitness_libs"))

from volumecalculator import VolumeCalculator

import discord
from discord.ext import commands
import spacy

class WorkoutAssistantCog(commands.Cog):
    """A Discord cog for replying to 'source that' message and displaying the content of the most relevant file."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.nlp = spacy.load("en_core_web_md")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listen for messages and reply to 'source that' message.

        Args:
            message (discord.Message): The message sent by a user.

        """
        if message.author == self.bot.user or not 'volume' in message.content.lower():
            return

        replied_message = message.reference.resolved if message.reference else None
        if not replied_message:
            return

        min_sets_per_week, max_sets_per_week = VolumeCalculator.get_sets_per_week(replied_message.content)
        if min_sets_per_week == max_sets_per_week:
            await message.channel.send(f"Sets in this program: {min_sets_per_week}")
            return
        else:
            await message.channel.send((f"Minimum sets: {min_sets_per_week}\n"
                                        f"Maximum sets: {max_sets_per_week}"))
            return

async def setup(bot: commands.Bot):
    """Setup function to add the SourceCog cog to the bot.

    Args:
        bot (commands.Bot): The bot instance.

    """
    await bot.add_cog(WorkoutAssistantCog(bot))
