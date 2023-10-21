from pathlib import Path
from typing import Any, Dict, Final

import discord
import yaml
from discord.ext import commands

CONFIG_PATH: Final[str] = Path("config.yaml")
"""
The bot config path
"""

def has_bot_input_perms(ctx: commands.Context):
    """
    Checks if the user has the bot-input role.
    """

    role = discord.utils.get(ctx.guild.roles, name="bot-input")
    return role in ctx.author.roles

def get_config() -> Dict[str, Any]:
    """
    Gets the config file contents that contain the data folder path
    """

    with open(CONFIG_PATH, "r") as config_file:
        return yaml.safe_load(config_file)