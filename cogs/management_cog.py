import discord
from discord.ext import commands

def has_bot_input_perms(ctx):
    role = discord.utils.get(ctx.guild.roles, name="bot-input")
    return role in ctx.author.roles

class ManagementCog(commands.Cog):
    def __init__(self, client):    
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Module: {self.qualified_name}")
    
    @commands.command()
    async def restart_bots(self, ctx):
        breakpoint()

async def setup(client):
    await client.add_cog(ManagementCog(client))
