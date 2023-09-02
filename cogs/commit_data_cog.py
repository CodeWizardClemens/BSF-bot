import discord
from discord.ext import commands, tasks
import subprocess

class CommitDataCog(discord.Cog):
    """A discord cog that commits user data to the BSF-bot-data repository via Git"""
    timezone = datetime.timezone.utc
    commit_time = datetime.datetime(hour=20, minute=30, tzinfo=timezone)

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data_folder = "./BSF-bot-data/weightcog/"

    @tasks.loop(time=commit_time)
    async def commit_data():
        datetime_now = datetime.now()
        current_date = datetime_now.strftime('%Y-%m-%d')
        current_time = datetime_now.strftime('%H-%M-%S')
        
        commit_msg = f"'(UTC: {current_date} {current_time}) Committing user data'"
        subprocess.run(["git", "add", self.data_folder])
        subprocess.run(["git", "commit", "-m", commit_msg])
        subprocess.run(["git", "push"])
