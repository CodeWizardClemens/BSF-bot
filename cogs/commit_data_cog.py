import datetime
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Final

import discord
from discord.ext import commands, tasks
import yaml

class CommitDataCog(commands.Cog):
    """
    Commits user data to the BSF-bot-data repository via Git. 
    
    It assumes that Git has already been setup on a host with access to the remote repository and that the setup won't change during runtime.
    """

    # Specifies the time to commit data through specified timezone, hour and minute values
    TIMEZONE: Final[datetime.timezone] = datetime.timezone.utc
    COMMIT_TIME: Final[datetime.time] = datetime.time(hour=14, minute=8, tzinfo=TIMEZONE)

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.CONFIG_PATH: Final[str] = Path("./config.yaml")
        self.config : Dict[str, Any] = self.get_config()
        self.DATA_PATH: Final[str] = self.config["data-folder"]
        
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
    Commits data according to COMMIT_TIME where Git is used to push changes to the remote repository
    """
    @tasks.loop(time=COMMIT_TIME)
    async def commit_data(self) -> None:
        datetime_now: datetime.datetime = datetime.datetime.now()
        current_date: str = datetime_now.strftime('%Y-%m-%d')
        current_time: str = datetime_now.strftime('%H-%M-%S')
        
        commit_msg: str = f"(UTC: {current_date} {current_time}) Committing user data" 

        # Gets the current working directory of the subprocess/bot instance NOT the working directory of the root process
        working_dir = os.getcwd()
        try:
            # Changes the current directory to the data folder if possible
            os.chdir(self.DATA_PATH)
        except FileNotFoundError as e:  
            print(f"Git could not find the data folder {self.DATA_PATH}.")

        self.commit_to_git(commit_msg)
        # Exits out of the BSF-bot-data directory back into BSF-bot
        os.chdir(working_dir)

    """
    Gets the config file contents that contain the data folder path
    """
    def get_config(self) -> Dict[str, Any]:
        with open(self.CONFIG_PATH, 'r') as config_file:
            return yaml.safe_load(config_file)

    """
    Runs the console commands to add, commit and push to Git
    """
    def commit_to_git(self, commit_msg : str) -> None:
        # Ensure that the repo is up to date first
        subprocess.run(["git", "fetch"])
        subprocess.run(["git", "checkout", "origin/master"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", commit_msg])
        subprocess.run(["git", "push", "origin", "HEAD:master"])

    """
    Checks if git is installed by checking the version
    """
    def is_git_installed(self) -> bool:
        try:
            subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            # TODO: Do we use logging instead?
            if e.returncode == 127:
                print("ERROR: Git isn't installed. Please install Git on the host or ensure the PATH variable has been set properly.")
            else:
                print(f"ERROR: Unknown. Return code: {e.returncode}")
                print(f"Standard output: {e.stdout}")
                print(f"Standard error: {e.stderr}")

            return False
        return True

"""Adds cog to the bot"""
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CommitDataCog(bot))
