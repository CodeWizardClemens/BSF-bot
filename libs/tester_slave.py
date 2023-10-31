from pathlib import Path
from typing import Callable, Final

import discord
import yaml
from discord import Message
from discord.ext.commands import Bot, Cog

"""
This module contains the tester slave bot and environments for testing on Discord.
"""


class TesterSlaveCog(Cog):
    def __init__(self, client: Bot, steps: Callable, responces: list[Message]) -> None:
        """
        Initializes a TesterSlaveCog instance.

        :param client: The Discord client instance.
        :param steps: A callable function for test steps.
        :param responses: A list to store received responses.
        """
        self.client = client
        self.steps = steps
        self.responces = responces

    @Cog.listener()
    async def on_ready(self):
        """
        When the client is ready, execute the test and clean up.
        """
        self.test_channel: int = self.client.get_channel(
            yaml.safe_load(Path("config_instance.yaml").open())["test_channel"]
        )
        await self.steps(self)
        await self.client.close()

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """
        When a message is send it is appended to the responses list.

        :param message: The received message.
        """
        if self.client.user == message.author:
            return
        self.responces.append(message)


class TesterSlaveEnvironment:
    """
    This class represents the environment for the tester slave bot.
    """

    def __init__(self):
        """
        Initializes a TesterSlaveEnvironment instance.

        :param client: The Discord bot instance.
        :param TOKEN: The Discord bot token.
        :param responses: A list to store received responses.
        """
        self.client = Bot(command_prefix="*", intents=discord.Intents.all())
        self.TOKEN: Final[str] = yaml.safe_load(Path("discord_token.yaml").open())[
            "discord_token_test_slave"
        ]
        self.responces: list[Message] = []

    async def start(self, steps: Callable) -> None:
        """
        Setup the environment and start the bot.

        :param steps: A function which will be executed in the bot. This function should contain the
                      steps that have to be taken to test the bot.
        """
        await self.client.add_cog(TesterSlaveCog(self.client, steps, self.responces))
        await self.client.start(self.TOKEN)

