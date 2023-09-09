import discord
from discord.ext import commands
import re

class ConversionCog(commands.Cog):
    """A Discord cog for converting height and weight values to metric units."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listen to messages and convert height and weight values.

        Args:
            message (discord.Message): The message sent by a user.

        """
        if message.author == self.bot.user:
            return

        content = message.content

        # Find matches of height and weight values in the message content
        height_matches = re.findall(r"(\d+)\s?['’]\s?(\d+)\s?(?:\"|inches?)?", content, re.IGNORECASE)
        weight_matches = re.findall(r"(\d+(?:\.\d+)?)\s?(?:lbs?|pounds?)", content, re.IGNORECASE)

        converted_content = content

        # Convert height values from feet and inches to centimeters (cm)
        for feet, inches in height_matches:
            total_inches = int(feet) * 12 + int(inches)
            cm = round(total_inches * 2.54)
            converted_height = f"{cm} cm "
            converted_content = re.sub(fr"(\d+)\s?['’]\s?(\d+)\s?(?:\"|inches?)?", converted_height, converted_content)

        # Convert weight values from pounds to kilograms (kg)
        for pounds in weight_matches:
            kg = round(float(pounds) * 0.45359237, 1)
            converted_weight = f"{kg} kg"
            converted_content = re.sub(fr"(\d+(?:\.\d+)?)\s?(?:lbs?|pounds?)", converted_weight, converted_content)

        # Send the converted message back to the channel
        if converted_content != content:
            await message.channel.send(f"```{converted_content}```")

async def setup(bot: commands.Bot):
    """Setup function to add the ConversionCog cog to the bot.

    Args:
        bot (commands.Bot): The bot instance.

    """
    await bot.add_cog(ConversionCog(bot))
