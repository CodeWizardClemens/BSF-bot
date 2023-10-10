import asyncio

import pytest

from libs.tester_slave import TesterSlaveCog, TesterSlaveEnvironment

"""
This module contains the test cases for the FunnyReactionsCog.
"""


@pytest.fixture
def tester_slave_environment() -> TesterSlaveEnvironment:
    """
    An environment which sets up a tester slave.

    :returns: The environment.
    """
    return TesterSlaveEnvironment()


@pytest.mark.skip("FIXME: The buzzwords don't seem to get added.")
@pytest.mark.asyncio
async def test_funny_reactions_cog(tester_slave_environment: TesterSlaveEnvironment):
    """
    Test the FunnyReactionsCog.
    """

    buzzwords = [
        (1, "eddie"),
        (2, "water"),
        (3, "thor"),
        (4, "fart"),
        (5, "strong"),
        (6, "deadlift"),
    ]

    reactions = [
        "<:eddiearm:794302033523245075>",
        "<:armeddie:794302066201853962>",
        "<:eddieshitting:794198092525338654>",
    ]

    async def steps(self: TesterSlaveCog):
        """
        Send a message in the test channel.
        """

        for _, message_to_send in buzzwords:
            await self.test_channel.send(message_to_send)
            await asyncio.sleep(1)

    await tester_slave_environment.start(steps)

    for index, buzzword in enumerate(buzzwords):
        message_reactions = tester_slave_environment.responces[index].reactions
        for reaction in reactions:
            assert reaction in message_reactions
