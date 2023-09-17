#!/usr/bin/env python3

import asyncio
import os
from pathlib import Path
from typing import Final

import discord
import yaml
from discord.ext import commands
from dotenv import load_dotenv
from pydub import AudioSegment

TOKEN: Final[str] = yaml.safe_load(Path("discord_token.yaml").open())["discord_token"]

client = commands.Bot(command_prefix=".", intents=discord.Intents.all())


@client.command(brief="Load clog module")
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")


@client.command(brief="Unload clog module")
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")


@client.command(brief="Reload all modules", aliases=["r"])
async def reload(ctx):
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.unload_extension(f"cogs.{filename[:-3]}")
            client.load_extension(f"cogs.{filename[:-3]}")
    await ctx.send("Reloaded cogs")


@client.command(brief="List modules to load/unload")
async def list_cogs(ctx):
    msg = ""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            msg += f"\n{filename[:-3]}"
    await ctx.send(msg)


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")


async def main():
    async with client:
        await load_extensions()
        await client.start(TOKEN)


asyncio.run(main())
