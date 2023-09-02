import discord
from discord.ext import commands
import os
import spacy

class SourceCog(commands.Cog):
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
        if message.author == self.bot.user:
            return

        content = message.content.lower()

        if 'source that' in content:
            replied_message = message.reference.resolved if message.reference else None
            if replied_message:
                relevant_file = await self.search_files(replied_message.content)
                if relevant_file:
                    file_content = await self.get_file_content(relevant_file)
                    if file_content:
                        channel = message.channel
                        await channel.send(f"Content of the most relevant file ({relevant_file}):\n{file_content}\n")

    async def search_files(self, input_text):
        relevant_file = None
        max_similarity = 0.0
        file_dir = "./data/info_commands"

        # Preprocess the input text
        input_doc = self.nlp(input_text)

        # Iterate through each file in the directory
        for file_name in os.listdir(file_dir):
            if file_name.endswith(".txt"):
                file_path = os.path.join(file_dir, file_name)

                # Read the contents of the file
                with open(file_path, "r") as file:
                    content = file.read()

                    # Preprocess the file content
                    content_doc = self.nlp(content)

                    # Calculate the similarity between input text and file content
                    similarity = input_doc.similarity(content_doc)

                    # Update the most relevant file if similarity is higher
                    if similarity > max_similarity:
                        max_similarity = similarity
                        relevant_file = file_name

        return relevant_file

    async def get_file_content(self, file_name):
        file_path = os.path.join("./data/info_commands", file_name)
        try:
            with open(file_path, "r") as file:
                content = file.read()
                return content
        except FileNotFoundError:
            return None

async def setup(bot: commands.Bot):
    """Setup function to add the SourceCog cog to the bot.

    Args:
        bot (commands.Bot): The bot instance.

    """
    await bot.add_cog(SourceCog(bot))
