import os
from typing import List
import discord
from discord.ext import commands


class InfoCommands(commands.Cog):
    """A Discord cog for managing information commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.save_directory = "./BSF-bog-data/info_commands/"
        os.makedirs(self.save_directory, exist_ok=True)

    @commands.Cog.listener()
    async def on_ready(self):
        """Event that is triggered when the bot is ready."""
        print("Module: InfoCommands")

    @commands.command()
    @commands.has_role("bot-input")
    async def backup(self, ctx):
        if not os.path.isdir(self.save_directory):
            await ctx.send("Save directory not found.")
            return

        for filename in os.listdir(self.save_directory):
            file_path = os.path.join(self.save_directory, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r") as file:
                    contents = file.read()
                    message = f"**{filename[:-4]}**\n\n{contents}"
                    await ctx.send(message)

    @commands.has_role("bot-input")
    @commands.command()
    async def learn(self, ctx: commands.Context, command: str, *, message: str) -> None:
        """Learn a new command and save it to a file.

        Args:
            ctx (commands.Context): The command context.
            command (str): The name of the command.
            message (str): The content of the command.

        """
        filename = f"{self.save_directory}{command.lower()}.txt"
        with open(filename, "w") as file:
            file.write(message)
        await ctx.send(f"Command '{command.lower()}' learned and saved.")

    @commands.command()
    async def list(self, ctx: commands.Context) -> None:
        """List all saved commands in alphabetical order.
    
        Args:
            ctx (commands.Context): The command context.
    
        """
        files = sorted([file[:-4] for file in os.listdir(self.save_directory) if file.endswith(".txt")])
        if files:
            file_list = " ".join(files)
            await ctx.send(f"```Saved commands:\n{file_list}```")
        else:
            await ctx.send("No commands saved yet.")
    
    @commands.command()
    async def whatis(self, ctx: commands.Context, command: str) -> None:
        """Display the content of a saved command.

        Args:
            ctx (commands.Context): The command context.
            command (str): The name of the command to display.

        """
        filename = f"{self.save_directory}{command}.txt"
        if os.path.isfile(filename):
            with open(filename, "r") as file:
                content = file.read()
            await ctx.send(content)
        else:
            await ctx.send(f"No command named '{command}' found.")

    @commands.command()
    async def rm(self, ctx: commands.Context, command: str) -> None:
        """Remove a saved command file.

        Args:
            ctx (commands.Context): The command context.
            command (str): The name of the command to remove.

        """
        filename = f"{self.save_directory}{command}.txt"
        if os.path.isfile(filename):
            with open(filename, "r") as file:
                content = file.read()
            await ctx.send(f"Showing the command one last time\n {content}")
            os.remove(filename)
            await ctx.send(f"Command '{command}' removed.")
        else:
            await ctx.send(f"No command named '{command}' found.")


async def setup(client: commands.Bot) -> None:
    """Setup function to add the InfoCommands cog to the bot.

    Args:
        client (commands.Bot): The bot instance.

    """
    await client.add_cog(InfoCommands(client))
