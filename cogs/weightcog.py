import csv
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Final, List

import discord
import matplotlib.pyplot as plt
import numpy as np
import yaml
from discord.ext import commands

"""
Discord cog module that stores, reads and removes weight data.
This cog can be loaded using an extension.
"""


def has_bot_input_perms(ctx):
    """
    Checks if the user has the bot-input role.
    """

    role = discord.utils.get(ctx.guild.roles, name="bot-input")
    return role in ctx.author.roles


class WeightCog(commands.Cog):
    """
    Discord cog that stores, reads and removes weight data.
    It also can make time series plots that record weight change over time.
    """

    MOVING_AVG_PERIODS: Final[Dict[str, int]] = {
        "weekly_avg": 7,
        "last_week": 7,
        "monthly_avg": 30,
        "last_month": 30,
        "yearly_avg": 365,
        "last_year": 365,
    }
    """
    Moving average period types and their corresponding integer values.
    """

    HEADER_ROW: Final[List[str]] = ["Date", "Weight"]
    """
    Header row of a user weight csv file.
    """

    CONFIG_PATH: Final[str] = Path("config.yaml")
    """
    The bot config path
    """

    def __init__(self, bot: commands.Bot):
        self.BOT = bot
        self.CONFIG: Final[Dict[str, Any]] = self.get_config()
        self.WEIGHT_COG_DATA_PATH: Final[str] = self.CONFIG["weight-cog-data-path"]

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Outputs the module name when the bot is ready."""

        print(f"Module: {self.__class__.__name__}")

    @commands.command()
    async def weight_goal(
        self, ctx: commands.Context, weight: float, user: discord.Member, date: str = None
    ) -> None:
        """
        Records a weight goal for a user.

        Usage:
          .weight <weight> <date> <user>
        Example:
          .weight 75.5 2023-08-27 @user

        Args:
            weight: (float): The weight value to be recorded.
            date: (str, optional): The date of the weight entry (default: current date).
            user: (discord.Member, optional): The user for whom the weight is being recorded
                  (default: yourself).
        """

        if user and (user != ctx.author) and not has_bot_input_perms(ctx):
            await ctx.send(
                "You don't have the bot-input role and are therefore not allowed to specify other"
                " users."
            )
            return

        try:
            weight: float = float(weight)
        except ValueError:
            await ctx.send("Not a valid weight.")

        user = user or ctx.author
        user_id: str = str(user.id)
        if not date:
            date = str(ctx.message.created_at.date())

        file_path = os.path.join(self.data_folder, f"{user_id}_goal_weight.csv")

        # Read existing entries
        entries = []
        header_row = ["Date", "Weight"]

        if os.path.exists(file_path):
            with open(file_path, "r") as csvfile:
                csv_reader = csv.reader(csvfile)
                header_row = next(csv_reader)  # Read the header row
                for row in csv_reader:
                    entries.append(row)

        # Add the new entry
        entries.append([date, weight])

        # Sort entries by date
        entries.sort(key=lambda entry: entry[0])

        # Rewrite the CSV file with sorted entries
        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header_row)  # Write header row
            csv_writer.writerows(entries)

        await ctx.send(f"Weight goal recorded for {date} ({user.display_name}): {weight} kg.")

    @commands.command()
    async def weight(
        self, ctx, weight: float, user: discord.Member = None, date: str = None
    ) -> None:
        """
        Records a user's weight.

        Usage:
        .weight <weight> [user] [date]
        Example:
        .weight 75.5 @user 2023-08-27

        Args:
            weight: (float) The weight value to be recorded.
            user: (discord.Member, optional): The user for whom the weight is being recorded
                  (default: yourself).
            date: (str, optional) The date of the weight entry
                  (default: current date).

        """
        if user and (user != ctx.author) and not has_bot_input_perms(ctx):
            await ctx.send(
                "You don't have the bot-input role and are therefore not allowed to specify other"
                " users."
            )
            return

        try:
            weight = float(weight)
        except ValueError:
            await ctx.send("Not a valid weight.")
        user = user or ctx.author
        user_id = str(user.id)
        if not date:
            date = str(ctx.message.created_at.date())

        file_path = os.path.join(self.data_folder, f"{user_id}.csv")

        # Read existing entries
        entries = []
        header_row = ["Date", "Weight"]

        if os.path.exists(file_path):
            with open(file_path, "r") as csvfile:
                csv_reader = csv.reader(csvfile)
                header_row = next(csv_reader)  # Read the header row
                for row in csv_reader:
                    entries.append(row)

        # Add the new entry
        entries.append([date, weight])

        # Sort entries by date
        entries.sort(key=lambda entry: entry[0])

        # Rewrite the CSV file with sorted entries
        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header_row)  # Write header row
            csv_writer.writerows(entries)
        await ctx.send(f"Weight recorded for {date} ({user.display_name}): {weight} kg.")

    def date_inside_period(self, period: str, date: date) -> bool:
        """
        Check if a date is inside of a period.
        Args:
            period (str): The period being referred to
            date (str): The date that may or may not be inside a period

        Returns True if date is inside a period.
        """
        today = datetime.now().date()

        if period == "all":
            return True

        try:
            days = WeightCog.MOVING_AVG_PERIODS[period]
            time_delta: timedelta = timedelta(days)
        except ValueError:
            raise ValueError(f"Invalid period: {period}.")

        start = today - time_delta
        return start <= date <= today

    # TODO: Put this function into WeightRepository
    def read_weight_data(self, user_weight_path: str, period):
        """
        Reads all of the user weight data relevant inside a period

        Args:
            user_weight_path (str): The path to the user's weight data
            period (): The period to read the weight data inside of (e.g. week, month, year)

        Returns the user's weight data from a period
        """
        user_weight_data_from_period = []
        with open(user_weight_path, "r") as csvfile:
            csv_reader: csv.reader = csv.reader(csvfile)
            # Skips the header row
            next(csv_reader)
            for row in csv_reader:
                if row == WeightCog.HEADER_ROW:
                    continue
                date: datetime = datetime.strptime(row[0], "%Y-%m-%d").date()
                if self.date_inside_period(period, date):
                    weight = float(row[1])
                    user_weight_data_from_period.append((date, weight))

        return user_weight_data_from_period

    def create_weight_plot(
        self, dates, weights, user, moving_averages=None, moving_avg_dates=None
    ) -> None:
        """
        Creates a time series line plot of how weight increases over time with the option to create
        a moving average line.

        Args:
            dates (): The dates extracted from the weight entries.
            weights (): The weights extracted from the weight entries.
            user (): The details of the user (we use the display name).
            moving_averages (| None): The moving averages for each weight data point.
            moving_avg_dates (| None): The moving average dates for each weight entry.
        """

        has_moving_averages: bool = moving_averages is not None and moving_avg_dates is not None

        plt.figure(figsize=(10, 6))
        # Weight data
        plt.plot(dates, weights, marker="o", color="red", linewidth=3)
        if has_moving_averages:
            # Moving average data
            plt.plot(
                moving_avg_dates,
                moving_averages,
                color="white",
                linewidth=3,
                label="Moving Average",
            )

        plt.xlabel("Date", fontsize=16, color="white")
        plt.ylabel("Weight (kg)", fontsize=16, color="white")
        plt.title(f"Weight Record for {user.display_name}", fontsize=18, color="white")
        plt.xticks(rotation=45, fontsize=12, color="white")
        plt.yticks(fontsize=12, color="white")
        plt.gca().spines["top"].set_visible(False)
        plt.gca().spines["right"].set_visible(False)
        plt.gca().spines["bottom"].set_color("white")
        plt.gca().spines["left"].set_color("white")
        plt.gca().tick_params(axis="x", colors="white")
        plt.gca().tick_params(axis="y", colors="white")
        plt.tight_layout()

        if has_moving_averages:
            plt.legend()

    # TODO: Put this code into a WeightRepository
    def remove_weight_record(
        self, user_weights_path: str, temp_user_weights_path: str, date: date
    ) -> bool:
        """
        Removes the weight record for a user on a specific date

        Args:
            user_weights_path (str): Path for a user's weight data
            temp_user_weights_path (str): Temporary path for a user's weight data. We then use this
                                          to replace the original weight path
            date (date): The date of the weight record to remove

        Returns the boolean result of whether the weight record was found and removed.
        """

        removed = False
        with open(user_weights_path, "r") as input_file, open(
            temp_user_weights_path, "w", newline=""
        ) as output_file:
            csv_reader: csv.reader = csv.reader(input_file)
            csv_writer: csv.writer = csv.writer(output_file)

            for row in csv_reader:
                if row[0] == date:
                    removed = True
                else:
                    csv_writer.writerow(row)

        os.replace(temp_user_weights_path, user_weights_path)
        return removed

    def get_config(self) -> Dict[str, Any]:
        """
        Gets the config file contents that contain the data folder path
        """

        with open(WeightCog.CONFIG_PATH, "r") as config_file:
            return yaml.safe_load(config_file)

    @commands.command()
    async def stats(
        self,
        ctx: commands.Context,
        moving_average: str = "no_avg",
        period: str = "last_month",
        user: discord.Member = None,
    ):
        """
        Displays a time series line graph showing the user's weight over time. It supports an
        optional moving average to calculate the moving average based on periods.

        This requires Qt platform plugin "wayland".

        Usage:

        .stats <moving_average> <period> <user>

        Examples:

        1. Display your stats:
        .stats

        2. Don't display averages for the weights you tracked last month.
        .stats no_avg last_month

        3. Display the weekly average for a user for the weight they tracked last year.
        .stats weekly_avg last_year @username

        Args:
            moving_average (str): Moving average period specified (or no_avg)
            period (str): Period of data to display. This is used for displaying stats WITHOUT a
                          moving average.
            user (discord.Member): A mention to a Discord user
        """

        if user and (user != ctx.author) and not has_bot_input_perms(ctx):
            await ctx.send(
                "You don't have the bot-input role and are therefore not allowed to specify other"
                " users."
            )
            return

        user = user or ctx.author
        user_id = str(user.id)
        file_path = os.path.join(self.data_folder, f"{user_id}.csv")

        if not os.path.exists(file_path):
            await ctx.send("No weight data found for this user.")
            return

        # Read weight data from CSV, skipping the header row
        data = []
        with open(file_path, "r") as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                date = datetime.strptime(row[0], "%Y-%m-%d").date()
                if self.date_inside_period(period, date):
                    weight = float(row[1])
                    data.append((date, weight))

        # Separate dates and weights
        dates, weights = zip(*data)

        # Calculate the moving average based on the provided argument
        if moving_average != "no_avg":
            if moving_average == "weekly_avg":
                moving_avg_period = 7  # 7 days for weekly average
            elif moving_average == "monthly_avg":
                moving_avg_period = 30  # Approximately 30 days for monthly average
            elif moving_average == "yearly_avg":
                moving_avg_period = 365  # 365 days for yearly average
            else:
                await ctx.send(
                    "Invalid moving average. Use 'weekly_avg', 'monthly_avg', or 'yearly_avg'."
                )
                return

            moving_averages = []
            for i in range(len(weights) - moving_avg_period + 1):
                avg = np.mean(weights[i : i + moving_avg_period])
                moving_averages.append(avg)

            # Adjust dates to match the moving average data length
            moving_avg_dates = dates[moving_avg_period - 1 :]

            # Create and save the plot with moving average
            plt.figure(figsize=(10, 6))
            plt.plot(
                dates, weights, marker="o", color="red", linewidth=3, label="Weight"
            )  # Weight data
            plt.plot(
                moving_avg_dates,
                moving_averages,
                color="white",
                linewidth=3,
                label="Moving Average",
            )  # Moving average
            plt.xlabel("Date", fontsize=16, color="white")
            plt.ylabel("Weight (kg)", fontsize=16, color="white")
            plt.title(f"Weight Record for {user.display_name}", fontsize=18, color="white")
            plt.xticks(rotation=45, fontsize=12, color="white")
            plt.yticks(fontsize=12, color="white")
            plt.gca().spines["top"].set_visible(False)
            plt.gca().spines["right"].set_visible(False)
            plt.gca().spines["bottom"].set_color("white")
            plt.gca().spines["left"].set_color("white")
            plt.gca().tick_params(axis="x", colors="white")
            plt.gca().tick_params(axis="y", colors="white")
            plt.legend()
            plt.tight_layout()

        else:
            # Create and save the plot without moving average
            plt.figure(figsize=(10, 6))
            plt.plot(dates, weights, marker="o", color="red", linewidth=3)  # Weight data
            plt.xlabel("Date", fontsize=16, color="white")
            plt.ylabel("Weight (kg)", fontsize=16, color="white")
            plt.title(f"Weight Record for {user.display_name}", fontsize=18, color="white")
            plt.xticks(rotation=45, fontsize=12, color="white")
            plt.yticks(fontsize=12, color="white")
            plt.gca().spines["top"].set_visible(False)
            plt.gca().spines["right"].set_visible(False)
            plt.gca().spines["bottom"].set_color("white")
            plt.gca().spines["left"].set_color("white")
            plt.gca().tick_params(axis="x", colors="white")
            plt.gca().tick_params(axis="y", colors="white")
            plt.tight_layout()

        plot_path = os.path.join(self.data_folder, f"{user_id}_plot.png")
        plt.savefig(plot_path, transparent=True)
        plt.close()

        # Send the plot as an embedded image
        plot_embed = discord.Embed(title=f"Weight Record for {user.display_name}")
        plot_embed.set_image(url="attachment://plot.png")
        await ctx.send(file=discord.File(plot_path, "plot.png"))

    @commands.command()
    async def remove_weight(self, ctx, date: str, user: discord.Member = None) -> None:
        """
        Remove a specific weight entry.

        Args:
            date: (str): The date of the weight entry to be removed.
            user: (discord.Member, optional): The user for whom the weight entry should be removed
                  (default: yourself).

        Usage:
        .remove_weight <date> [user]
        Example:
        .remove_weight 2023-08-27 @user
        """

        if user and (user != ctx.author) and not has_bot_input_perms(ctx):
            await ctx.send(
                "You don't have the bot-input role and are therefore nore allowed to specify other"
                " users."
            )
            return

        user = user or ctx.author
        user_id: str = str(user.id)
        user_weights_path: str = os.path.join(self.WEIGHT_COG_DATA_PATH, f"{user_id}.csv")
        temp_user_weights_path: str = os.path.join(self.WEIGHT_COG_DATA_PATH, f"{user_id}_temp.csv")

        if not os.path.exists(user_weights_path):
            await ctx.send("No weight data found for this user.")
            return

        removed = False
        with open(user_weights_path, "r") as input_file, open(
            temp_user_weights_path, "w", newline=""
        ) as output_file:
            csv_reader = csv.reader(input_file)
            csv_writer = csv.writer(output_file)

            # Write header row
            # csv_writer.writerow(["Date", "Weight"])

            for row in csv_reader:
                if row[0] == date:
                    await ctx.send(f"Weight record for {row[0]} ({row[1]} kg) removed.")
                    removed = True
                else:
                    csv_writer.writerow(row)

        os.replace(temp_user_weights_path, user_weights_path)
        if not removed:
            await ctx.send(f"No weight record found for the date {date}.")
        else:
            await ctx.send(f"Weight record for {date} removed.")

    @commands.command()
    async def export(self, ctx: commands.Context, user: discord.Member = None) -> None:
        """
        Export weight data as a CSV file.

        Arguments:
            user (discord.Member, optional): The user for whom the weight data should be exported.
                 (default: yourself)

        Usage:
        .export [user]
        Example:
        .export @user
        """

        if user and (user != ctx.author) and not has_bot_input_perms(ctx):
            await ctx.send(
                "You don't have the bot-input role and are therefore not allowed to specify other"
                " users."
            )
            return

        user = user or ctx.author
        user_id = str(user.id)
        file_path = os.path.join(self.data_folder, f"{user_id}.csv")

        if not os.path.exists(file_path):
            await ctx.send("No weight data found for this user.")
            return

        # Check permissions for exporting other users' data
        if user != ctx.author and not ctx.author.guild_permissions.administrator:
            await ctx.send("You don't have the necessary permissions to export other users' data.")
            return

        # Send the CSV file as an attachment
        with open(file_path, "rb") as csv_file:
            await ctx.send(
                f"Weight data for {user.display_name}",
                file=discord.File(csv_file, filename=f"{user.display_name}_weight_data.csv"),
            )

    @commands.command()
    async def delete_all_user_data(
        self, ctx: commands.Context, user: discord.Member = None
    ) -> None:
        """
        Deletes all log data related to weight only (CSV file) associated with a
        specified Discord user or the command invoker.

        Parameters:
            ctx (commands.Context): The context of the command.
            user (discord.Member, optional): The Discord user for whom to delete the log data. Defaults to the command invoker.
        Example:
            .del_all_log
            .del_all_log user(Optional)
        """
        if user and (user != ctx.author) and not has_bot_input_perms(ctx):
            await ctx.send(
                "You don't have the bot-input role and are therefore not allowed to specify"
                " other users."
            )
            return

        user = user or ctx.author
        user_id = str(user.id)
        file_path = os.path.join(self.data_folder, f"{user_id}.csv")

        # if the file/data for user does not exist
        if not os.path.exists(file_path):
            await ctx.send("No weight data found for this user.")
            return
        else:
            embed = discord.Embed(
                title=f"Are you sure you want to remove all user weight data for @{user}",
                timestamp=datetime.utcnow(),
                colour=discord.Colour.blurple(),
            )
            embed.set_thumbnail(url=user.avatar)
            msg = await ctx.send(embed=embed)
            for emoji in ["✅", "❌"]:
                await msg.add_reaction(emoji)

            def option_check(reaction, user):  # a check function which takes the user's response
                return user == ctx.author and reaction.emoji in ["✅", "❌"]

            option, _ = await self.BOT.wait_for("reaction_add", check=option_check, timeout=30)
            if option.emoji == "✅":
                os.remove(file_path)
                embed = discord.Embed(
                    title=f"All logs have been deleted",
                    timestamp=datetime.utcnow(),
                    colour=discord.Colour.blurple(),
                )
                await ctx.send(embed=embed)
                return
            else:
                embed = discord.Embed(
                    title=f"Operation Cancelled",
                    timestamp=datetime.utcnow(),
                    colour=discord.Colour.blurple(),
                )
                await ctx.send(embed=embed)
                return


async def setup(bot: commands.Bot):
    """Setup function to add the ConversionCog cog to the bot.

    Args:
        bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(WeightCog(bot))
