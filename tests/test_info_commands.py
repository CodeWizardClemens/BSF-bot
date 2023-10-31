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


# @pytest.mark.skip("FIXME: Test doesn't work")
@pytest.mark.asyncio
async def test_conversion_cog(tester_slave_environment: TesterSlaveEnvironment):
    """
    Test the conversion cog.
    """

    async def steps(self: TesterSlaveCog):
        """
        Send a message in the test channel.
        """
        # tester_slave_environment.responces[responce_index].content
        # XXX: This test may fail if a previous test has not been cleaned up properly in a test
        # environment. This can be fixed when the cog has easier to set up states. For now it should
        # be payed attention to if it does ever fail.
        await self.test_channel.send(".learn test_command_for_integration This is the expected data"
                                     " I want to get returned.")
        await asyncio.sleep(1)
        assert self.responces[0].content == ("Command 'test_command_for_integration' learned and"
                                             " saved.")
        
        await self.test_channel.send(".whatis test_command_for_integration")
        await asyncio.sleep(1)
        assert self.responces[1].content == "This is the expected data I want to get returned."

        await self.test_channel.send(".rm test_command_for_integration")
        await asyncio.sleep(2)

        await asyncio.sleep(1)
        assert self.responces[2].content == "Command 'test_command_for_integration' removed."

    await tester_slave_environment.start(steps)
