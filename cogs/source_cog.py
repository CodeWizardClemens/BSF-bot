import discord
from discord.ext import commands
import os
import spacy

class SourceCog(commands.Cog):
    """
    A Discord cog for replying to 'source that' message and displaying the content of the most relevant file.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.nlp = spacy.load("en_core_web_md")
        self.CONFIG_PATH: Final[str] = Path("./BOT_CONFIG.yaml")
        self.config : Dict[str, Any] = self.get_config()
        self.info_commands_path : str = self.config["info-commands-path"]

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

        if 'source that' in lowercase_content:
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
        relevant_file = None
        max_similarity = 0.0

        # Preprocess the input text
        input_doc = self.nlp(input_text)

        # Iterate through each file in the directory
        saved_files : List[str] = os.listdir(self.info_commands_path)
        txt_files : List[str] = sorted([file[:-4] for file in saved_files if file.endswith(".txt")])
        for file_name in txt_files:
            file_path = os.path.join(self.info_commands_path, file_name)

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

    # TODO: Get rid of useless function?
    async def get_file_content(self, file_name):
        file_path = os.path.join(self.info_commands_path, file_name)
        try:
            with open(file_path, "r") as file:
                content = file.read()
                return content
        except FileNotFoundError:
            return None

async def setup(bot: commands.Bot) -> None:
    """
    Setup function to add the SourceCog cog to the bot.

    Args:
        bot (commands.Bot): The bot instance.

    """
    await bot.add_cog(SourceCog(bot))
