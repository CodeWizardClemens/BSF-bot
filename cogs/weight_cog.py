import discord
from discord.ext import commands
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Final, Any
from pathlib import Path
import yaml

def has_bot_input_perms(ctx):
    role = discord.utils.get(ctx.guild.roles, name="bot-input")
    return role in ctx.author.roles

class WeightCog(commands.Cog):
    MOVING_AVG_PERIODS : Final[Dict[str, int]] = {
        "weekly_avg": 7, "last_week": 7,
        "monthly_avg": 30, "last_month": 30,
        "yearly_avg": 365, "last_year": 365
    }
    # Header row of a user weight csv file
    HEADER_ROW : Final[List[str]] = ["Date", "Weight"] 
    
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.CONFIG_PATH: Final[str] = Path("./BOT_CONFIG.yaml")
        self.config : Dict[str, Any] = self.get_config()
        self.WEIGHT_COG_DATA_PATH : Final[str] = self.config["weight-cog-data-path"]

    @commands.command()
    async def weight_goal(self, ctx : commands.Context, weight: float, user: discord.Member, date: str = None) -> None:
        """
        Records a weight goal for a user.

        Usage:
        .weight <weight> <date> <user>
        Example:
        .weight 75.5 2023-08-27 @user

        Parameters:
        :param weight: (float) The weight value to be recorded.
        :param date: (str, optional) The date of the weight entry (default: current date).
        :param user: (discord.Member, optional): The user for whom the weight is being recorded (default: yourself).
        """
    
        if user and (user != ctx.author) and not has_bot_input_perms(ctx):
            await ctx.send(f"You don't have the bot-input role and are therefore not allowed to specify other users")
            return

        try:
            weight : float = float(weight)
        except:
            await ctx.send(f"Not a valid weight.")
    
        user = user or ctx.author
        user_id : str = str(user.id)
        if not date:
            date : str = str(ctx.message.created_at.date())
    
        user_weight_path : str = os.path.join(self.WEIGHT_COG_DATA_PATH, f"{user_id}_goal_weight.csv")

        new_entries = self.insert_weight_entry(date, weight, user_weight_path)
        self.sort_weight_entries(user_weight_path, new_entries)

        await ctx.send(f"Weight goal recorded for {date} ({user.display_name}): {weight} kg.")

    @commands.command()
    async def weight(self, ctx, weight: float, user: discord.Member = None, date: str = None):
        """
        Records a user's weight

        Usage:
        .weight <weight> [user] [date]
        Example:
        .weight 75.5 @user 2023-08-27

        Parameters:
        :param weight: (float) The weight value to be recorded.
        :param user: (discord.Member, optional): The user for whom the weight is being recorded (default: yourself).
        :param date: (str, optional) The date of the weight entry (default: current date).

        """
        if user and (user != ctx.author) and not has_bot_input_perms(ctx):
            await ctx.send(f"You don't have the bot-input role and are therefore not allowed to specify other users")
            return

        try:
            weight = float(weight)
        except:
            await ctx.send(f"Not a valid weight.")

        user = user or ctx.author
        user_id = str(user.id)
        if not date:
            date = str(ctx.message.created_at.date())
    
        user_weight_path = os.path.join(self.WEIGHT_COG_DATA_PATH, f"{user_id}.csv")

        new_entries = self.insert_weight_entry(date, weight, user_weight_path)
        self.sort_weight_entries(user_weight_path, new_entries)
        await ctx.send(f"Weight recorded for {date} ({user.display_name}): {weight} kg.")

    # TODO: Put this into WeightRepository
    def sort_weight_entries(self, user_weight_path : str, entries) -> None:
        """
        Sorts the weight entries by date and overwrites the CSV file with the sorted entries
        """
        # Sort entries by date
        entries.sort(key=lambda entry: entry[0])
        # Overwrite the CSV file with sorted entries
        with open(user_weight_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            # Writes the header row
            csv_writer.writerow(WeightCog.HEADER_ROW)
            csv_writer.writerows(entries)

    # TODO: Put this into WeightRepository
    def insert_weight_entry(self, date : date, weight : float, user_weight_path):
        """
        Reads the existing entries in the user_weight_path and inserts a new weight entry
        """
        # Read existing entries
        entries = []

        if os.path.exists(user_weight_path):
            with open(user_weight_path, "r") as csvfile:
                csv_reader : csv.reader = csv.reader(csvfile)
                for row in csv_reader:
                    entries.append(row)

        entries.append([date, weight])
        return entries

    def date_inside_period(self, period: str, date: date) -> bool:
        """
        Check if a date is inside of a period.

        :returns: True if date is inside a period.
        """
        today = datetime.now().date()

        if period == "all":
            return True

        try:
            days = WeightCog.MOVING_AVG_PERIODS[period]
            time_delta : timedelta = timedelta(days)
        except:
            raise ValueError(f"Invalid period: {period}.")

        start = today - time_delta
        return start <= date <= today

    # TODO: Put this function into WeightRepository
    def read_weight_data(self, user_weight_path : str, period):
        """
        Reads all of the user weight data relevant inside a period
        """
        user_weight_data = []
        with open(user_weight_path, "r") as csvfile:
            csv_reader : csv.reader = csv.reader(csvfile)
            # Skips the header row
            next(csv_reader)
            for row in csv_reader:
                if row == WeightCog.HEADER_ROW: continue
                date : date = datetime.strptime(row[0], "%Y-%m-%d").date()
                if self.date_inside_period(period, date):
                    weight : float = float(row[1])
                    user_weight_data.append((date, weight))

        return user_weight_data

    """
    Creates a time series line plot of how weight increases over time with the option to create a moving average line
    """
    def create_weight_plot(self, dates, weights, user, moving_averages = None, moving_avg_dates = None) -> None:
        has_moving_averages = moving_averages != None and moving_avg_dates != None

        plt.figure(figsize=(10, 6))
        # Weight data
        plt.plot(dates, weights, marker='o', color='red', linewidth=3)
        if has_moving_averages:
            # Moving average
            plt.plot(moving_avg_dates, moving_averages, color='white', linewidth=3, label='Moving Average')

        plt.xlabel("Date", fontsize=16, color='white')
        plt.ylabel("Weight (kg)", fontsize=16, color='white')
        plt.title(f"Weight Record for {user.display_name}", fontsize=18, color='white')
        plt.xticks(rotation=45, fontsize=12, color='white')
        plt.yticks(fontsize=12, color='white')
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['bottom'].set_color('white')
        plt.gca().spines['left'].set_color('white')
        plt.gca().tick_params(axis='x', colors='white')
        plt.gca().tick_params(axis='y', colors='white')
        plt.tight_layout()

        if has_moving_averages:
            plt.legend()

    # TODO: Put this code into a WeightRepository
    def remove_weight_record(self, user_weights_path : str, temp_user_weights_path : str, date : date) -> bool:
        """
        Removes the weight record for a user on a specific date
        """
        removed = False
        with open(user_weights_path, "r") as input_file, open(temp_user_weights_path, "w", newline="") as output_file:
            csv_reader : csv.reader = csv.reader(input_file)
            csv_writer : csv.writer = csv.writer(output_file)

            for row in csv_reader:
                if row[0] == date:
                    removed = True
                else:
                    csv_writer.writerow(row)

        os.replace(temp_user_weights_path, user_weights_path)
        return removed

    """
    Gets the config file contents that contain the data folder path
    """
    def get_config(self) -> Dict[str, Any]:
        with open(self.CONFIG_PATH, 'r') as config_file:
            return yaml.safe_load(config_file)

    @commands.command()
    async def stats(
            self, ctx : commands.Context,
            moving_average: str = commands.parameter(
                default="no_avg",
                description="Options: weekly_avg, monthly_avg, yearly_avg, no_avg."),
            period: str = commands.parameter(
                default="last_month",
                description="Which data to dosplay. Options: last_week, last_month, last_year, all"),
            user: discord.Member = commands.parameter(
                default=None,
                description="A mention to a discord user."),
            ) -> None:
        """
        Displays a time series line graph showing the user's weight over time. It supports an optional moving average to calculate the moving average based on periods.

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
        """

        if user and (user != ctx.author) and not has_bot_input_perms(ctx):
            await ctx.send("You don't have the bot-input role and are therefore not allowed to specify other users")
            return
    
        user = user or ctx.author
        user_id : str = str(user.id)
        user_weight_path : str = os.path.join(self.WEIGHT_COG_DATA_PATH, f"{user_id}.csv")
    
        if not os.path.exists(user_weight_path):
            await ctx.send("No weight data found for this user.")
            return

        # Read weight data from CSV, skipping the header row
        user_weight_data = self.read_weight_data(user_weight_path, period)
        # Separate dates and weights
        dates, weights = zip(*user_weight_data)
        if moving_average == "no_avg":
            self.create_weight_plot(dates, weights, user)
        else:
            try:
                moving_avg_period : int = WeightCog.MOVING_AVG_PERIODS[moving_average]
            except:
                await ctx.send("Invalid moving average. Use 'weekly_avg', 'monthly_avg', or 'yearly_avg'.")
                return
            
            moving_averages : List[float] = []
            # Calculates the moving averages based on the selected moving average period
            for i in range(len(weights) - moving_avg_period + 1):
                avg = np.mean(weights[i:i + moving_avg_period])
                moving_averages.append(avg)

            # Adjust dates to match the moving average data length
            moving_avg_dates : List[date] = dates[moving_avg_period - 1:]
            self.create_weight_plot(dates, weights, user, moving_averages, moving_avg_dates)

        # Saves plot
        plot_path : str = os.path.join(self.WEIGHT_COG_DATA_PATH, f"{user_id}_plot.png")
        plt.savefig(plot_path, transparent=True)
        plt.close()

        await ctx.send(file=discord.File(plot_path, "plot.png"))

    @commands.command()
    async def remove_weight(self, ctx, date: str, user: discord.Member = None) -> None:
        """
        Remove a specific weight entry.

        :param date: (str): The date of the weight entry to be removed.
        :param user: (discord.Member, optional): The user for whom the weight entry should be removed (default: yourself).

        Usage:
        .remove_weight <date> [user]
        Example:
        .remove_weight 2023-08-27 @user
        """

        if user and (user != ctx.author) and not has_bot_input_perms(ctx):
            await ctx.send(f"You don't have the bot-input role and are therefore nore allowed to specify other users")
            return


        user = user or ctx.author
        user_id : str = str(user.id)
        user_weights_path : str = os.path.join(self.WEIGHT_COG_DATA_PATH, f"{user_id}.csv")
        temp_user_weights_path : str = os.path.join(self.WEIGHT_COG_DATA_PATH, f"{user_id}_temp.csv")

        if not os.path.exists(user_weights_path):
            await ctx.send("No weight data found for this user.")
            return

        record_removed : bool = self.remove_weight_record(user_weights_path, temp_user_weights_path, date)
        if not record_removed:
            await ctx.send(f"No weight record found for the date {date}.")
        else:
            await ctx.send(f"Weight record for {date} ({weight} kg) removed.")

    # TODO: This code can be put into WeightRepository
    @commands.command()
    async def export(self, ctx, user: discord.Member = None) -> None:
        """
        Export weight data as a CSV file.
    
        Parameters:
        - user (discord.Member, optional): The user for whom the weight data should be exported (default: yourself).
    
        Usage:
        .export [user]
        Example:
        .export @user
        """
    
        if user and (user != ctx.author) and not has_bot_input_perms(ctx):
            await ctx.send("You don't have the bot-input role and are therefore not allowed to specify other users")
            return
    
        user = user or ctx.author
        user_id : str = str(user.id)
        user_weights_path : str = os.path.join(self.WEIGHT_COG_DATA_PATH, f"{user_id}.csv")
    
        if not os.path.exists(user_weights_path):
            await ctx.send("No weight data found for this user.")
            return
    
        has_permissions : bool = user == ctx.author and ctx.author.guild_permissions.administrator
        if not has_permissions:
            await ctx.send("You don't have the necessary permissions to export other users' data.")
            return
    
        # Send the CSV file as an attachment
        with open(user_weights_path, "rb") as csv_file:
            csv_attachment : discord.File = discord.File(csv_file, filename=f"{user.display_name}_weight_data.csv")
            await ctx.send(f"Weight data for {user.display_name}", file=csv_attachment)

async def setup(bot: commands.Bot) -> None:
    """Setup function to add the ConversionCog cog to the bot.

    Args:
        bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(WeightCog(bot))
