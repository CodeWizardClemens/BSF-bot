# BSF bot
This is a repository for the BSF-Bot which is a Discord "fitness" bot that can be used for many purposes related to health and fitness such as:

- Converting imperial units into metric units, outputting a converted message to save people from having to manually convert units
- Tracking weight data over time and allowing users to display statistics for their weight data
- Calculate and display relevant metrics such as FFMI and BMI based on inputs given
- Info commands that can be used to retrieve information about a topic
and many other features!

The BSF-Bot is primarily used for the BSF Fitness Discord server.

## What is the BSF Fitness community?
The BSF Fitness community is devoted to bringing positive change in your life and fitness goals. Including help with your overall health, nutrition, and athletic training.

Misinformation is a disease. Our goal is to clear up the misinformation that has been popping up in the fitness community, which leaves beginners clueless on what direction to go in. We are an evidence-based community that does not tolerate misinformation.

Join if you are passionate about making a change in your life and learning from others within our community.

This server offers professional services, these include meal plans, sport-related dieting, physique transformations, improving health, and energy levels, advice on weekly intakes, etc (from certified/registered practitioners).

Discord link: https://discord.gg/bsf-fitness-688710650507165697

https://bsffitness.weebly.com/



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

After this add the following lines to the `config_instance.yaml` file:

```yaml
# config_instance.yaml
"test_channel": <channel id were you want to preform the tests>
"debug": True
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
