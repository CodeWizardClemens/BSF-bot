import discord
from discord.ext import commands
from typing import Final, Dict, Any
import yaml

# TODO: Could we add support for multiple polls?
class PollsCog(commands.Cog):
    """
    A cog for creating polls for a specified channel ID
    """
    # Thumbs emojis for adding reactions to polls
    THUMBS : Final[Dict[str,str]] = {
        "thumbs_up": '\N{THUMBS UP SIGN}',
        "thumbs_down": '\N{THUMBS DOWN SIGN}'
    }

    def __init__(self, bot):    
        self.bot = bot
        self.config = self.get_config()
        # Default channel for polls
        self.POLLS_CHANNEL_ID : Final[int] = self.config["polls_channel_id"]

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Displays the module name in the console once the cog is ready
        """
        print("Module: {self.class_name}")

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        # Creates poll based off thumbs up/down THUMBS
        if(message.channel.id == self.POLLS_CHANNEL_ID):
            await message.add_reaction(PollsCog.THUMBS["thumbs_up"])
            await message.add_reaction(PollsCog.THUMBS["thumbs_down"])

    """
    Gets the config file contents that contain the data folder path
    """
    def get_config(self) -> Dict[str, Any]:
        with open(self.CONFIG_PATH, 'r') as config_file:
            return yaml.safe_load(config_file)

async def setup(bot) -> None:
    await bot.add_cog(PollsCog(bot))
