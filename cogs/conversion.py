import re

import discord
from discord.ext import commands


class ConversionCog(commands.Cog):
    """
    A Discord cog for converting height and weight values to metric units.
    """

    # Compiled regular expressions as it may improve performance slightly
    HEIGHT_PATTERN: re.Pattern = re.compile(r"(\d+)\s?['’]\s?(\d+)\s?", re.IGNORECASE)
    WEIGHT_PATTERN: re.Pattern = re.compile(r"(\d+(?:\.\d+)?)\s?(?:lbs?|pounds?)", re.IGNORECASE)

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

        content: str = message.content

        # Converts the imperial units to metric units
        converted_heights = ConversionCog.HEIGHT_PATTERN.sub(self.convert_height_to_cm, content)
        converted_weights = ConversionCog.WEIGHT_PATTERN.sub(
            self.convert_weight_to_kg, converted_heights
        )

        # Send the converted message back to the channel
        if converted_weights != content:
            await message.channel.send(f"```{converted_weights}```")

    def convert_height_to_cm(self, match: re.Match) -> str:
        """
        Regex callback function that converts each height match into a centimeter value, returning the height converted string.

        Args:
            match (re.Match): The match found by the height regex
        """

        feet: int = int(match.group(1))
        inches: int = int(match.group(2))
        if feet is None or match.group(2) is None:
            return

        total_inches: int = feet * 12 + inches
        cm: int = round(total_inches * 2.54)
        return f"{cm} cm "

    def convert_weight_to_kg(self, match: re.Match) -> str:
        """
        Regex callback function that converts each `lb` match into a `kg` value, returning the weight converted string.

        Args:
            match (re.Match): The match found by the weight regex
        """

        lbs: float = float(match.group(1))
        if lbs is None:
            return

        kg: float = round(lbs * 0.45359237, 1)
        return f"{kg} kg"


async def setup(bot: commands.Bot) -> None:
    """
    Setup function to add the ConversionCog cog to the bot.

    Args:
        bot (commands.Bot): The bot instance.

    """
    await bot.add_cog(ConversionCog(bot))
