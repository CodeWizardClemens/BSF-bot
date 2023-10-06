# BSF bot

## Setting up the bot

To authenticate the bot a `discord_token.yaml` file needs to be created with a Discord token:
```yaml
# discord_token.yaml
discord_token: <your discord token>
```

## Running the tests

The tests are done via a tester slave, which talks to the bot and expects a certain responce back.

Add the following line to  `discord_token.yaml` to authenticate the tester slave:

```yaml
# discord_token.yaml
discord_token_test_slave: <your discord token>
```

After this add the following line to the `config_instance.yaml` file:

```yaml
# config_instance.yaml
"test_channel": <channel id were you want to preform the tests>
```

Now you are able to run the tests with the following command:

```
nox --session tests
```


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
