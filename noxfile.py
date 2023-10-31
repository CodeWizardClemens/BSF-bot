import subprocess
import time

import nox

"""
Configuration file for Nox.

To run the Nox environment simply run:

    nox

View all possible commands:

    nox --list

Run a specific command from the list:

    nox --session <command> <command> ...
    nox -s <command> ...
    nox -e <command> ...

View the Nox help pages:

    nox --help
"""

def bot_kill(c, bot_name: str) -> None:
    """
    Kill a bot's screen session if it exists.

    :param bot_name: The name of the bot. This is also the name of the screen session.
    """
    if is_screen_session_running(bot_name):
        # Specify (-S) the name of the bot to screen and execute (-X) a quit command.
        c.run(f"screen -S {bot_name} -X quit")

def is_screen_session_running(screen_name: str) -> bool:
    """
    Check if a screen with a specific name is running.

    This can be checked by running the "screen -ls" command, which outputs all the current running
    screens. This output is filered to see if #screen_name matches it.

    Example output from screen -ls:

    There are screens on:
        882444.pts-2.hp (Attached)
        881967.bot1     (Detached)
        879711.bot2     (Detached)
    3 Sockets in /run/screens/S-m.
    """
    # The screen command returns a non-zero exit code when no screens are running. This causes the
    # subprocess to fail. If this happens the the expected error message should be "No Sockets
    # found". In this case no screens are running and the function should return false.
    try:
        screen_output = subprocess.check_output(
            ["screen", "-ls"], stderr=subprocess.STDOUT, text=True
        )
    except subprocess.CalledProcessError as screen_error:
        if "No Sockets found" in screen_error.output:
            return False  # No active screens found
        raise RuntimeError(
            "The 'screen' command was not able to get the current running screens"
        )

    # Split the output by line and iterate through screen names.
    for line in screen_output.splitlines():
        if line.startswith("\t"):
            # Extract the screen name.
            current_screen_name = line.strip().split(".")[1].split("\t")[0]
            if current_screen_name == screen_name:
                return True

    # If no exact match is found, return False
    return False


@nox.session
def format(session):
    """
    Run code formatter.
    """

    # TODO turn black back on.
    # session.install("black")
    # session.run("black", "./")

    session.install("isort")
    session.run("isort", "./")


@nox.session
def checkers(session):
    """
    Run all checkers.
    """

    # TODO Test of adding the bandit tool adds vallue to the checkers. It is fairly slow, but might
    # help with writing more secure code.
    # session.install("bandit")

    # TODO turn black back on.
    # session.install("black")
    # session.run("black", "--check", "./")
    session.install("isort")
    session.run("isort", "--check", "./")

    session.install("ruff")
    session.run("ruff", "./")

    # TODO, Turn pylint on, and add more checkers.
    # session.install("pylint")
    # session.run("pylint", "./**/*.py")


@nox.session
def tests(session):
    """`
    Run all tests.

    This command starts up the BSF bot and a tester slave so create a test environment.

    """
    bot_screen_name = "debug-BSF-bot-for-tests"
    if is_screen_session_running(bot_screen_name):
        bot_kill(bot_screen_name)
    
    # -d = Detach the screen, -S = specify a name, -m = The command to run.
    process = subprocess.Popen(["screen", "-d", "-S", bot_screen_name, "-m", "./BSF-bot.py"])
    process.wait()

    # FIXME: Find some kind of mutex to make this work instead of a delay.
    time.sleep(5)
    assert process.returncode == 0, (f"Expected screen for `{bot_screen_name}` to be started. But"
                                    "the screen comnmand returned a non zero value.")

    session.install("pytest")
    session.install("discord", "pyyaml", "pytest-asyncio")

    session.run("pytest", "./tests")

    # -S = specify a name, -X execute a a command.
    result = subprocess.run(["screen", "-S" , bot_screen_name, "-X" , "quit"])
    assert result.returncode == 0 or is_screen_session_running(bot_screen_name),(
        f"Expected screen for `{bot_screen_name}` to be closed. But the screen comnmand returned a"
        " non zero value.")
