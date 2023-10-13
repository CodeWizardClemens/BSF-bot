#!/usr/bin/env python3

import asyncio
import os
from pathlib import Path
from typing import Final

import discord
import yaml
from discord.ext.commands import Bot, DefaultHelpCommand
from discord.message import Message

"""
The executable script for the BSF bot.
"""

class DebugBot(Bot):
    """
    A debugable version of the Discord `Bot` class.

    This class is needed to overwrite the `process_commands` function. This function stops the
    invokation of commands, when the caller is another bot. This functionality is needed to run
    integration tests with tester slaves.
    """
    async def process_commands(self, message: Message, /) -> None:
        """
        This function processes the commands that have been registered
        to the bot and other groups. Without this coroutine, none of the
        commands will be triggered.

        :param message: A discord message.
        """

        if message.author == self.user:
             return

        ctx = await self.get_context(message)
        # the type of the invocation context's bot attribute will be correct
        await self.invoke(ctx)  # type: ignore

run_debug_bot = yaml.safe_load(Path("config_instance.yaml").open())["debug"]
bot_class = DebugBot if run_debug_bot else Bot
client = bot_class(command_prefix=".", intents=discord.Intents.all())

TOKEN: Final[str] = yaml.safe_load(Path("discord_token.yaml").open())["discord_token"]
client.help_command = DefaultHelpCommand(show_parameter_descriptions=False)


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
