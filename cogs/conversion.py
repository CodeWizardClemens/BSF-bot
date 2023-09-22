import re
from typing import List, Tuple

import discord
from discord.ext import commands


class ConversionCog(commands.Cog):
    """
    A Discord cog for converting height and weight values to metric units.
    """

    # Compiled regular expressions as it may improve performance slightly
    HEIGHT_PATTERN: re.Pattern = re.compile(
        r"(\d+)\s?['’]\s?(\d+)\s?(?:\"|inches?)?", re.IGNORECASE
    )
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

        height_matches: List[Tuple[str, str]] = ConversionCog.HEIGHT_PATTERN.findall(content)
        weight_matches: List[str] = ConversionCog.WEIGHT_PATTERN.findall(content)

        # Converts the imperial units to metric units
        converted_content: str = self.convert_height_to_cm(
            self.convert_lbs_to_kgs(content, weight_matches), height_matches
        )

        # Send the converted message back to the channel
        if converted_content != content:
            await message.channel.send(f"```{converted_content}```")

    def convert_height_to_cm(self, content: str, height_matches: List[str]) -> str:
        """
        Convert height values from feet and inches to centimeters (cm)

        Args:
            content (str): The message content sent by the user containing possible feet and inches
            height_matches (): Regex matches that have been identified by self.height_regex
        """
        converted_content: str = content
        for feet, inches in height_matches:
            total_inches: int = int(feet) * 12 + int(inches)
            cm: int = round(total_inches * 2.54)
            converted_height: str = f"{cm} cm"
            converted_content: str = ConversionCog.HEIGHT_PATTERN.sub(
                self.converted_height, converted_content
            )

        return converted_content

    def convert_lbs_to_kgs(self, content: str, weight_matches: List[str]) -> str:
        """
        Convert weight values from pounds to kilograms (kg)


        Args:
            content (str): The message content sent by the user containing possible feet and inches
            weight_matches (): Regex matches that have been identified by self.weight_regex
        """
        converted_content: str = content
        for pounds in weight_matches:
            kg = round(float(pounds) * 0.45359237, 1)
            converted_weight: str = f"{kg} kg"
            converted_content: str = ConversionCog.WEIGHT_PATTERN.sub(
                converted_weight, converted_content
            )

        return converted_content


async def setup(bot: commands.Bot) -> None:
    """
    Setup function to add the ConversionCog cog to the bot.

    Args:
        bot (commands.Bot): The bot instance.

    """
    await bot.add_cog(ConversionCog(bot))
