#!/usr/bin/env python3

import asyncio
import logging
import os
from pathlib import Path
from typing import Final

import discord
import asyncpg
import yaml
from discord.ext import commands
from models.model import Model


TOKEN: Final[str] = yaml.safe_load(Path("discord_token.yaml").open())["discord_token"]
URI: Final[str] = yaml.safe_load(Path("discord_token.yaml").open())["uri"]


client = commands.Bot(command_prefix=".", intents=discord.Intents.all())
log = logging.getLogger(__name__)


async def prepare_postgres(postgres_uri: str, retries: int = 5, interval: float = 5.0, **cp_kwargs) -> bool:
    """
    Prepare the postgres database connection.

    :param str postgres_uri:  The postgresql URI to connect to.
    :param int retries:       Included to fix issue with docker starting API before DB is finished starting.
    :param float interval:    Interval of which to wait for next retry.
    """

    db_name = postgres_uri.split("/")[-1]
    db_log = logging.getLogger("DB")

    if Model.pool is not None:
        db_log.info("No need to create pool, it already exists!")
        return True

    db_log.info(f'Attempting to connect to DB "{db_name}"')
    for i in range(1, retries + 1):
        try:
            await Model.create_pool(uri=postgres_uri, **cp_kwargs)
            break

        except asyncpg.InvalidPasswordError as e:
            db_log.error(str(e))
            return False

        except (ConnectionRefusedError,):
            db_log.warning(f"Failed attempt #{i}/{retries}, trying again in {interval}s")

            if i == retries:
                db_log.error("Failed final connection attempt, exiting.")
                return False

            await asyncio.sleep(interval)

    db_log.info(f'Connected to database "{db_name}"')
    return True


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
    discord.utils.setup_logging()
    if not await prepare_postgres(
            URI,
            max_con=10,
            min_con=1,
    ):
        log.info("Not Connected to DB")

    async with client:
        await load_extensions()
        await client.start(TOKEN)


asyncio.run(main())
