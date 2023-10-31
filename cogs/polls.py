from pathlib import Path
from typing import Any, Dict, Final

import yaml
from discord.ext.commands.bot import Bot
from discord.ext.commands.cog import Cog
from discord.message import Message
from models.config import Config

"""
Module which contains a Cog for a bot to automatically create polls.
"""


# TODO: Extend the polls cog to work with mutiple channels.
# TODO: Replace the channel ID by an actual channel name. Or even better, allow a user to specify a
# channel per discord server, and save this channel in the bot data.
class PollsCog(Cog):
    """
    Cog for a bot to automatically create polls when a message is send in a specific channel with a
    channel ID (which is set as the variable `polls_channel_id` in the config.yaml file).
    """

    THUMBS: Final[Dict[str, str]] = {
        "thumbs_up": "\N{THUMBS UP SIGN}",
        "thumbs_down": "\N{THUMBS DOWN SIGN}",
    }
    """
    Codes for thumbs up and down emojis.
    """

    def __init__(self, bot):
        self.BOT: Final[Bot] = bot
        """
        The bot object itself.
        """

    @Cog.listener()
    async def on_ready(self) -> None:
        """
        Displays the module name in the console once the cog is ready.
        """
        print(f"Module: {self.__class__.__name__}")

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """
        Listener that gets called when a discord message is send in any channel that the bot is
        present in.
        """
        data = await Config.get(guild_id=message.guild.id)
        if message.channel.id == data.polls_channel_id:
            await PollsCog.create_poll(message)

    @classmethod
    async def create_poll(cls, message: Message) -> None:
        """
        Creates poll by responding to a message with a thumbs ups, and a thumbs down.

        :param message: A discord message.
        """
        await message.add_reaction(PollsCog.THUMBS["thumbs_up"])
        await message.add_reaction(PollsCog.THUMBS["thumbs_down"])


async def setup(bot) -> None:
    """
    Add PollsCog to a discord Bot.

    :param bot: The bot which PollsCog should be added too.
    """
    await bot.add_cog(PollsCog(bot))
