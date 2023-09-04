import discord
from discord.ext import commands, tasks
import subprocess
import datetime
import yaml
import os

class CommitDataCog(commands.Cog):
    """A discord cog that commits user data to the BSF-bot-data repository via Git"""
    timezone = datetime.timezone.utc
    commit_time = datetime.time(hour=20, minute=30, tzinfo=timezone)

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_loc = "./BOT_CONFIG.yaml"
        config_yaml = self.get_config_yaml()
        self.data_folder = config_yaml["data-folder"]

        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            # Do we use logging instead?
            ctx.send("Git isn't installed. Please install Git on the host.")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Module: CommitDataCog")

    @commands.command()
    async def start_commit_data(self, ctx):
        await self.commit_data()

    @tasks.loop(time=commit_time)
    async def commit_data(self, ctx):
        print("test0.5")
        try:
            datetime_now = datetime.datetime.now()
            current_date = datetime_now.strftime('%Y-%m-%d')
            current_time = datetime_now.strftime('%H-%M-%S')
        except Exception as e:
            print(e)
        
        print("test1")
        commit_msg = f"'(UTC: {current_date} {current_time}) Committing user data'"

        try:
            os.chdir(self.data_folder)
            subprocess.run(["git", "add", "."])
        except subprocess.CalledProcessError as e:
            # Do we use logging instead?
            ctx.send("Git could not find the data folder.")

        print("test2")
        subprocess.run(["git", "commit", "-m", commit_msg])
        print("test3")
        subprocess.run(["git", "push"])
        subprocess.run(["ls"])

    def get_config_yaml(self):
        with open(self.config_loc, 'r') as config_file:
            config_yaml = yaml.safe_load(config_file)
        return config_yaml

async def setup(bot):
    await bot.add_cog(CommitDataCog(bot))