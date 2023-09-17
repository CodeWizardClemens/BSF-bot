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

    CONFIG_PATH : Final[str] = Path("./config.yaml")
    """
    Configuration file path for the bot
    """

    KEY_PHRASE : Final[str] = 'source that'
    """
    Key phrase to listen to when sourcing information
    """

    PREPROCESS_PIPELINE : Final[spacy.lang.en.English] = spacy.load("en_core_web_md")
    """
    Medium English NLP pipeline that preprocesses text documents. It can also extract a similarity metric
    """

    def __init__(self, bot: commands.Bot):
        self.bot : commands.Bot = bot
        self.CONFIG : Final[Dict[str, Any]] = self.get_config()
        self.INFO_COMMANDS_PATH : Final[str] = self.CONFIG["info-commands-path"]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Listen for messages and replies to the 'source that' message with a relevant source. The user replies to a message with "source that" when they want a source.

        Args:
            message (discord.Message): The message sent by a user.

        """
        if message.author == self.bot.user:
            return

        lowercase_content = message.content.lower()
        # Checks if the key phrase is stated
        if SourceCog.KEY_PHRASE in lowercase_content:
            replied_message : bool = message.reference.resolved if message.reference else None
            # Checks if the user actually replied to a message
            if replied_message:
                relevant_file = await self.search_files(replied_message.content)
                # Has a relevant file been found?
                if relevant_file:
                    file_content = await self.get_file_content(relevant_file)
                    # Can the file content be extracted?
                    if file_content:
                        channel = message.channel
                        await channel.send(f"Content of the most relevant file ({relevant_file}):\n{file_content}\n")

    async def search_files(self, input_text : str):
        """
        Searches through all of the info command files to determine the most relevant file via the max similarity score. It assumes that the relevant info text file is in .txt format

        Args:
            input_text (str): Input text from the replied message
        """
        relevant_info_file = None
        max_similarity : float = 0.0

        # Preprocess the input text to later compute similarity
        preprocessed_input_doc : spacy.tokens.doc.Doc = SourceCog.PREPROCESS_PIPELINE(input_text)

        # Iterate through each file in the directory
        saved_files : List[str] = os.listdir(self.INFO_COMMANDS_PATH)
        txt_files : List[str] = sorted([file[:-4] for file in saved_files if file.endswith(".txt")])
        for info_file_name in txt_files:
            info_file_path : str = os.path.join(self.INFO_COMMANDS_PATH, f"{info_file_name}.txt")

            # Read the contents of the info command file
            with open(info_file_path, "r") as info_file:
                content = info_file.read()

                # Preprocess the file content
                content_doc : spacy.tokens.doc.Doc = SourceCog.PREPROCESS_PIPELINE(content)

                # Calculate the similarity between input text and file content
                similarity : float = preprocessed_input_doc.similarity(content_doc)

                # Update the most relevant file if similarity is higher
                if similarity > max_similarity:
                    max_similarity = similarity
                    relevant_info_file = info_file_name

        return relevant_info_file

    async def get_file_content(self, file_name : str):
        """
        Extracts file content through a specified file name.

        Args:
            file_name (str): Name of the file to extract content from
        """
        file_path : str = os.path.join(self.INFO_COMMANDS_PATH, file_name)
        try:
            with open(f"{file_path}.txt", "r") as file:
                content = file.read()
                return content
        except FileNotFoundError:
            return None

    def get_config(self) -> Dict[str, Any]:
        """
        Gets the config file contents that contain the data folder path
        """
        with open(SourceCog.CONFIG_PATH, 'r') as config_file:
            return yaml.safe_load(config_file)

async def setup(bot: commands.Bot) -> None:
    """
    Setup function to add the SourceCog cog to the bot.

    Args:
        bot (commands.Bot): The bot instance.

    """
    await bot.add_cog(SourceCog(bot))
