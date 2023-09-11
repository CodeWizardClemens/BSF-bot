# BSF bot

## Nox environment

The bot uses Nox to configure virtual environment, and manage the project itself. Nox is configured in `noxfile.py`.
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
