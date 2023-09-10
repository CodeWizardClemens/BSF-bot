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
def lint(session):
    """
    Run all linters.
    """
    session.install("ruff")
    session.install("flake8")
    session.install("pylint")

    session.run("ruff", "./")
    session.run("flake8")
    session.run("pylint *.py")
