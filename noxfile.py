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
    """
    Run all tests.
    """
    session.install("pytest")

    session.install("discord", "pyyaml", "pytest-asyncio")
    session.run("pytest", "./tests")
