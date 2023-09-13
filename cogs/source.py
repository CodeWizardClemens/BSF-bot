import discord
from discord.ext import commands
import os
import spacy
from pathlib import Path
from typing import Dict, Final, List, Any
import yaml

class SourceCog(commands.Cog):
    """
    A Discord cog for replying to 'source that' message and displaying the content of the most relevant file.
    """
    CONFIG_PATH : Final[str] = Path("./BOT_CONFIG.yaml")
    KEY_PHRASE : Final[str] = 'source that'

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.nlp = spacy.load("en_core_web_md")
        self.config : Dict[str, Any] = self.get_config()
        self.INFO_COMMANDS_PATH : Final[str] = self.config["info-commands-path"]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Listen for messages and reply to 'source that' message.

        Args:
            message (discord.Message): The message sent by a user.

        """
        if message.author == self.bot.user:
            return

        lowercase_content = message.content.lower()
        if SourceCog.KEY_PHRASE in lowercase_content:
            replied_message = message.reference.resolved if message.reference else None
            if replied_message:
                relevant_file = await self.search_files(replied_message.content)
                if relevant_file:
                    file_content = await self.get_file_content(relevant_file)
                    if file_content:
                        channel = message.channel
                        await channel.send(f"Content of the most relevant file ({relevant_file}):\n{file_content}\n")

    async def search_files(self, input_text):
        """
        Searches through all of the info command files to determine the most relevant file via the max similarity score
        """
        relevant_info_file = None
        max_similarity = 0.0

        # Preprocess the input text
        preprocessed_input_doc = self.nlp(input_text)

        # Iterate through each file in the directory
        saved_files : List[str] = os.listdir(self.INFO_COMMANDS_PATH)
        txt_files : List[str] = sorted([file[:-4] for file in saved_files if file.endswith(".txt")])
        for info_file_name in txt_files:
            info_file_path = os.path.join(self.INFO_COMMANDS_PATH, info_file_name)

            # Read the contents of the file
            with open(info_file_path, "r") as info_file:
                content = info_file.read()

                # Preprocess the file content
                content_doc = self.nlp(content)

                # Calculate the similarity between input text and file content
                similarity = preprocessed_input_doc.similarity(content_doc)

                # Update the most relevant file if similarity is higher
                if similarity > max_similarity:
                    max_similarity = similarity
                    relevant_info_file = info_file_name

        return relevant_info_file

    async def get_file_content(self, file_name : str):
        file_path : str = os.path.join(self.INFO_COMMANDS_PATH, file_name)
        try:
            with open(file_path, "r") as file:
                content = file.read()
                return content
        except FileNotFoundError:
            return None

    """
    Gets the config file contents that contain the data folder path
    """
    def get_config(self) -> Dict[str, Any]:
        with open(SourceCog.CONFIG_PATH, 'r') as config_file:
            return yaml.safe_load(config_file)

async def setup(bot: commands.Bot) -> None:
    """
    Setup function to add the SourceCog cog to the bot.

    Args:
        bot (commands.Bot): The bot instance.

    """
    await bot.add_cog(SourceCog(bot))
