import re

import discord
from discord.ext import commands

"""
Discord cog module for converting imperial units to metric.
This can be loaded via an extension.
"""


class ConversionCog(commands.Cog):
    """
    A Discord cog for converting height and weight values to metric units.
    """

    HEIGHT_PATTERN: re.Pattern = re.compile(r"(\d+)\s?['’]\s?(\d+)\s?", re.IGNORECASE)
    """
    Regex to extract the height in feet and inches from a string.

    For example:
    
    I am 23 inches -> 23
    I am 3 feet 3 inches-> 3, 3
    """

    WEIGHT_PATTERN: re.Pattern = re.compile(r"(\d+(?:\.\d+)?)\s?(?:lbs?|pounds?)", re.IGNORECASE)
    """
    Regex to extract the weight in pounds from a string.

    For example:
    I am a 184 pounds male -> 184
    I am a 225lbs male -> 225
    """

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Listen to messages and converts height and weight values.

        Args:
            message (discord.Message): The message sent by a user.

        """

        if message.author == self.bot.user:
            return

        # Converts the imperial units to metric units
        converted_heights = ConversionCog.HEIGHT_PATTERN.sub(
            self.convert_height_to_cm, message.content
        )
        converted_weights = ConversionCog.WEIGHT_PATTERN.sub(
            self.convert_weight_to_kg, converted_heights
        )

        msg_has_converted = converted_weights != message.content
        if msg_has_converted:
            await message.channel.send(f"```{converted_weights}```")

    def convert_height_to_cm(self, match: re.Match) -> str:
        """
        Regex callback function that converts each height match into a centimeter value.
        This returns the height converted string.

        Args:
            match (re.Match): The match found by the height regex.
            This should contain a feet and inches value.
        """

        assert match.group(1), "Expected the feet value to be not None"
        assert match.group(2), "Expected the inches value to be not None"

        feet = int(match.group(1))
        inches = int(match.group(2))

        total_inches = feet * 12 + inches
        cm = round(total_inches * 2.54)
        return f"{cm} cm "

    def convert_weight_to_kg(self, match: re.Match) -> str:
        """
        Regex callback function that converts each `lb` match into a `kg` value.
        This returns the weight converted string.

        Args:
            match (re.Match): The match found by the weight regex.
            This should should contain a `lbs` value.

        """

        assert match.group(1), "Expected the lbs value to be not None"

        lbs = float(match.group(1))

        kg = round(lbs * 0.45359237, 1)
        return f"{kg} kg"


async def setup(bot: commands.Bot) -> None:
    """
    Setup function to add the ConversionCog cog to the bot.

    Args:
        bot (commands.Bot): The bot instance.

    """
    await bot.add_cog(ConversionCog(bot))
