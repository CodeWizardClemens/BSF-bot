import asyncio

import pytest

from libs.tester_slave import TesterSlaveCog, TesterSlaveEnvironment

"""
This module contains the test cases for the conversion cog.
"""

@pytest.fixture
def tester_slave_environment() -> TesterSlaveEnvironment:
    """
    An environment which sets up a tester slave.

    :returns: The environment.
    """
    return TesterSlaveEnvironment()

@pytest.mark.asyncio
async def test_conversion_cog(tester_slave_environment: TesterSlaveEnvironment):
    """
    Test the conversion cog.
    """

    # TODO Update with better, and more, test values. Maybe even use a random function?
    test_values = [
        ("I am 200 lbs", "I am 90.7 kg"),
        ("I am 200lbs", "I am 90.7 kg"),
        ("I am 0lbs", "I am 0.0 kg"),
        ("I am -10lbs", "I am -4.5 kg"),
    ]

    async def steps(self: TesterSlaveCog):
        """
        Send a message in the test channel.
        """
        for message_to_send, _ in test_values:
            await self.test_channel.send(message_to_send)
            await asyncio.sleep(1)

    await tester_slave_environment.start(steps)

    for responce_index, test_value in enumerate(test_values):
        assert (
            tester_slave_environment.responces[responce_index].content == f"```{test_value[1]}```"
        )
