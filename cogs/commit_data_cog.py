import discord
from discord.ext import commands, tasks
import subprocess
import datetime
import yaml
import os
from typing import Dict, Any

class CommitDataCog(commands.Cog):
    """
    Commits user data to the BSF-bot-data repository via Git. 
    
    It assumes that Git has already been setup on a host with access to the remote repository.
    """

    # Specifies the time to commit data through a specified timezone
    timezone: datetime.timezone = datetime.timezone.utc
    commit_time: datetime.time = datetime.time(hour=20, minute=2, tzinfo=timezone)

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.config_loc: str = "./BOT_CONFIG.yaml"
        config_yaml: Dict[str, Any] = self.get_config_yaml()
        self.data_folder: str = config_yaml["data-folder"]

        self.commit_data.start()
        # Checks if git is installed
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            # TODO: Do we use logging instead?
            ctx.send("Git isn't installed. Please install Git on the host.")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Module: CommitDataCog")

    """Manually starts commit_data()"""
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
    def get_config_yaml(self) -> Dict[str, Any]:
        with open(self.config_loc, 'r') as config_file:
            config_yaml: Dict[str, Any] = yaml.safe_load(config_file)
        return config_yaml

"""Adds cog to the bot"""
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CommitDataCog(bot))