import shlex

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
    session.install("black")
    session.install("isort")

    session.run("black", "./")
    session.run("isort", "./")


@nox.session
def checkers(session):
    """
    Run all checkers.
    """
    session.install("black")
    session.install("isort")
    session.install("ruff")
    session.install("pylint")

    # TODO Test of adding the bandit tool adds vallue to the checkers. It is fairly slow, but might
    # help with writing more secure code.
    # session.install("bandit")

    session.run("black", "--check", "./")
    session.run("isort", "--check", "./")
    session.run("ruff", "./")
    session.run("pylint", "./**/*.py")
