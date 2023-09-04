import discord
from discord.ext import commands, tasks
import subprocess
import datetime
import yaml
import os
from typing import Dict, Any, Final

class CommitDataCog(commands.Cog):
    """
    Commits user data to the BSF-bot-data repository via Git. 
    
    It assumes that Git has already been setup on a host with access to the remote repository.
    """

    # Specifies the time to commit data through specified timezone, hour and minute values
    timezone: Final[datetime.timezone] = datetime.timezone.utc
    commit_time: Final[datetime.time] = datetime.time(hour=20, minute=27, tzinfo=timezone)

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.config_path: Final[str] = "./BOT_CONFIG.yaml"
        config: Dict[str, Any] = self.get_config()
        self.data_folder: Final[str] = config["data-folder"]
        
        # Only commits data if Git is installed on the host
        if (self.is_git_installed()): self.commit_data.start()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Module: CommitDataCog")

    """
    Manually starts commit_data()
    example: .start_commit_data
    """
    @commands.command()
    async def start_commit_data(self, ctx: commands.Context) -> None:
        await self.commit_data()

    """
    Commits data via Git to the remote data repository
    """
    @tasks.loop(time=commit_time)
    async def commit_data(self) -> None:
        datetime_now: datetime.datetime = datetime.datetime.now()
        current_date: str = datetime_now.strftime('%Y-%m-%d')
        current_time: str = datetime_now.strftime('%H-%M-%S')
        
        commit_msg: str = f"(UTC: {current_date} {current_time}) Committing user data" 

        # Changes the current directory to the data folder if possible
        try:
            os.chdir(self.data_folder)
        except FileNotFoundError as e:  
            print("Git could not find the data folder.")

        # Runs commands in console via subprocess
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", commit_msg])
        subprocess.run(["git", "push"])

    """Gets the config file contents that contain the data folder path"""
    def get_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as config_file:
            config_yaml: Dict[str, Any] = yaml.safe_load(config_file)
        return config_yaml

    """
    Checks if git is installed by checking the version
    """
    def is_git_installed(self) -> bool:
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            # TODO: Do we use logging instead?
            print("Git isn't installed. Please install Git on the host.")
            return False
        return True

"""Adds cog to the bot"""
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CommitDataCog(bot))