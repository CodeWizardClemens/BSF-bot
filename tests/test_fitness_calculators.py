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

    # FIXME The BMR calculator seems to be broken.
    test_values = [
        ("184cm 99kg", "BMI: 29.24"),
        ("100kg 100cm", "BMI: 100.00"),
        ("30bf 188cm 120kg", "BMI: 33.95\nFFMI: 23.80"),
    ]

    async def steps(self: TesterSlaveCog):
        """
        Send a message in the test channel.
        """
        for message_to_send, _ in test_values:
            await self.test_channel.send(message_to_send)
            await asyncio.sleep(2)

    await tester_slave_environment.start(steps)

    for responce_index, test_value in enumerate(test_values):
        assert (
            tester_slave_environment.responces[responce_index].content == test_value[1]
        )
