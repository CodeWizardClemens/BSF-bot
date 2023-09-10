import os
from typing import List
import discord
from discord.ext import commands
import yaml
from typing import Final, Dict, Any, List
from pathlib import Path

class InfoCommandsCog(commands.Cog):
    """
    A Discord cog for managing information commands.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.CONFIG_PATH: Final[str] = Path("./BOT_CONFIG.yaml")
        self.config : Dict[str, Any] = self.get_config()
        self.save_directory : str = self.config["save-directory-path"]
        os.makedirs(self.save_directory, exist_ok=True)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Outputs the module name when the bot is ready
        """
        print("Module: InfoCommands")

    # TODO: What does this command do?
    @commands.command()
    @commands.has_role("bot-input")
    async def backup(self, ctx):
        save_dir_found : bool = os.path.isdir(self.save_directory)
        if not save_dir_found:
            await ctx.send("Save directory not found.")
            return

        save_dir_files : List[str] = os.listdir(self.save_directory)
        for filename in save_dir_files:
            file_path = os.path.join(self.save_directory, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r") as file:
                    contents = file.read()
                    message = f"**{filename[:-4]}**\n\n{contents}"
                    await ctx.send(message)

    @commands.has_role("bot-input")
    @commands.command()
    async def learn(self, ctx: commands.Context, command: str, *, message: str) -> None:
        """
        Learns a new command and save it to a file.

        Args:
            ctx (commands.Context): The command context.
            command (str): The name of the command.
            message (str): The content of the command.

        """
        filename : str = f"{self.save_directory}{command.lower()}.txt"
        with open(filename, "w") as file:
            file.write(message)
        await ctx.send(f"Command '{command.lower()}' learned and saved.")

    @commands.command()
    async def list(self, ctx: commands.Context) -> None:
        """
        List all saved commands in alphabetical order.
    
        Args:
            ctx (commands.Context): The command context.
    
        """
        saved_files : List[str] = os.listdir(self.save_directory)
        txt_files : List[str] = sorted([file[:-4] for file in saved_files if file.endswith(".txt")])
        if txt_files:
            file_list : List[str] = " ".join(txt_files)
            await ctx.send(f"```Saved commands:\n{file_list}```")
        else:
            await ctx.send("No commands saved yet.")
    
    @commands.command()
    async def whatis(self, ctx: commands.Context, command: str) -> None:
        """
        Display the content of a saved command.

        Args:
            ctx (commands.Context): The command context.
            command (str): The name of the command to display.

        """
        filename : str = f"{self.save_directory}{command}.txt"
        if os.path.isfile(filename):
            with open(filename, "r") as file:
                content : str = file.read()
            await ctx.send(content)
        else:
            await ctx.send(f"No command named '{command}' found.")

    # TODO: Couldn't we just call whatis ontop of this and add os.remove()? We could return a boolean that indicates if the command exists too
    @commands.command()
    async def rm(self, ctx: commands.Context, command: str) -> None:
        """
        Remove a saved command file.

        Args:
            ctx (commands.Context): The command context.
            command (str): The name of the command to remove.

        """
        filename : str = f"{self.save_directory}{command}.txt"
        if os.path.isfile(filename):
            with open(filename, "r") as file:
                content : str = file.read()
            await ctx.send(f"Showing the command one last time\n {content}")

            os.remove(filename)
            await ctx.send(f"Command '{command}' removed.")
        else:
            await ctx.send(f"No command named '{command}' found.")

    """
    Gets the config file contents that contain the data folder path
    """
    def get_config(self) -> Dict[str, Any]:
        with open(self.CONFIG_PATH, 'r') as config_file:
            return yaml.safe_load(config_file)


async def setup(client: commands.Bot) -> None:
    """Setup function to add the InfoCommands cog to the bot.

    Args:
        client (commands.Bot): The bot instance.

    """
    await client.add_cog(InfoCommandsCog(client))
