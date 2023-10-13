import os
from pathlib import Path
from typing import Any, Dict, Final, List

import yaml
from discord.ext import commands

"""
Discord cog module that can be loaded through an extension. 
"""


class InfoCommandsCog(commands.Cog):
    """
    A Discord cog for managing information commands through CRUD operations. Users can use the
    information commands to learn about a topic.

    Example:

        .whatis carbs
        <Displays information about carbs>

    """

    CONFIG_PATH: Final[str] = Path("./config.yaml")
    """
    Bot configuration path used to get data directory paths.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config: Dict[str, Any] = self.get_config()
        self.INFO_COMMANDS_PATH: Final[Path] = Path(self.config["info-commands-path"])
        # Creates the info commands directory
        self.INFO_COMMANDS_PATH.touch()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Outputs the module name when the bot is ready."""

        print("Module: InfoCommands")

    @commands.has_role("bot-input")
    @commands.command()
    async def learn(self, ctx: commands.Context, command: str, *, message: str) -> None:
        """
        Learns a new command and save it to a file.

        Args:
            ctx (commands.Context): The command context.
            command (str): The name of the new info command.
            message (str): The content of the new info command.

        """

        info_filename: str = f"{self.INFO_COMMANDS_PATH}/{command.lower()}.txt"
        with open(info_filename, "w") as file:
            file.write(message)
        await ctx.send(f"Command '{command.lower()}' learned and saved.")

    @commands.command()
    async def list(self, ctx: commands.Context) -> None:
        """
        List all saved commands in alphabetical order.

        Args:
            ctx (commands.Context): The command context.

        """

        saved_info_files: List[str] = os.listdir(self.INFO_COMMANDS_PATH)
        info_txt_files: List[str] = sorted(
            [file[:-4] for file in saved_info_files if file.endswith(".txt")]
        )

        if info_txt_files:
            info_file_list: List[str] = " ".join(info_txt_files)
            await ctx.send(f"```Saved commands:\n{info_file_list}```")
        else:
            await ctx.send("No commands saved yet.")

    @commands.command()
    async def whatis(self, ctx: commands.Context, command: str) -> None:
        """
        Display the content of a saved command.

        Args:
            ctx (commands.Context): The command context.
            command (str): The name of the info command to display.

        """

        info_filename: str = f"{self.INFO_COMMANDS_PATH}/{command.lower()}.txt"
        if os.path.isfile(info_filename):
            with open(info_filename, "r") as file:
                content: str = file.read()
            await ctx.send(content)
        else:
            await ctx.send(f"No info command named '{command}' found.")

    # TODO: Issue-10 Extract conversion logic to a library
    @commands.command()
    async def rm(self, ctx: commands.Context, command: str) -> None:
        """
        Removes a saved info command file.

        Args:
            ctx (commands.Context): The command context.
            command (str): The name of the info command to remove.

        """

        info_filename: str = f"{self.INFO_COMMANDS_PATH}/{command.lower()}.txt"
        info_file_found: bool = os.path.isfile(info_filename)
        if info_file_found:
            os.remove(info_filename)
            await ctx.send(f"Command '{command}' removed.")
        else:
            await ctx.send(f"No command named '{command}' found.")

    def get_config(self) -> Dict[str, Any]:
        """
        Returns the config file contents that contain the data folder path.
        """
        with open(self.CONFIG_PATH, "r") as config_file:
            return yaml.safe_load(config_file)


async def setup(client: commands.Bot) -> None:
    """
    Setup function to add the InfoCommandsCog cog to the bot.

    Args:
        client (commands.Bot): The bot instance.

    """
    await client.add_cog(InfoCommandsCog(client))
