import asyncio

import pytest

from libs.tester_slave import TesterSlaveCog, TesterSlaveEnvironment

"""
This module contains the test cases for the PollsCog.
"""


@pytest.fixture
def tester_slave_environment() -> TesterSlaveEnvironment:
    """
    An environment which sets up a tester slave.

    :returns: The environment.
    """
    return TesterSlaveEnvironment()


@pytest.mark.skip("FIXME: Cog currently does not support setting poll channel by command. This"
                  "makes it so that poll tests are difficult to setup..")
@pytest.mark.asyncio
async def test_polls_cog(tester_slave_environment: TesterSlaveEnvironment):
    """
    Test the PollsCog.
    """

    test_messages = [
        (1, "Is maingaining a viable method for building muscle?"),
        (2, "Is the risk to reward ratio for conventional deadlifts not worth it?"),
    ]

    reactions = [
        "\N{THUMBS UP SIGN}",
        "\N{THUMBS DOWN SIGN}",
    ]

    async def steps(self: TesterSlaveCog):
        """
        Send a message in the test channel.
        """

        for _, message_to_send in test_messages:
            await self.test_channel.send(message_to_send)
            await asyncio.sleep(1)

    await tester_slave_environment.start(steps)

    for index, _ in enumerate(test_messages):
        message_reactions = tester_slave_environment.responces[index].reactions
        for reaction in reactions:
            assert reaction in message_reactions
