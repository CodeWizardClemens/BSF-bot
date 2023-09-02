import discord
from discord.ext import commands
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta, date


def has_bot_input_perms(ctx):
    role = discord.utils.get(ctx.guild.roles, name="bot-input")
    return role in ctx.author.roles

class WeightCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = "./BSF-bot-data/weightcog/"

    @commands.command()
    async def weight_goal(self, ctx, weight: float, date: str = None, user: discord.Member = None):
        """
        Record your a weight goal.

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

        assert date
        assert weight

        try:
            weight = float(weight)
        except:
            await ctx.send(f"Not a valid weight.")
    
        user = user or ctx.author
        user_id = str(user.id)
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
    async def weight(self, ctx, weight: float, user: discord.Member = None, date: str = None):
        """
        Record your daily weight.

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

        :returns: True if date is inside a period.
        """
        today = datetime.now().date()

        if period == "last_week":
            last_week_start = today - timedelta(days=7)
            return last_week_start <= date <= today
        elif period == "last_month":
            last_month_start = today - timedelta(days=30)
            return last_month_start <= date <= today
        elif period == "last_year":
            last_year_start = today - timedelta(days=365)
            return last_year_start <= date <= today
        elif period == "all":
            return True
        else:
            raise ValueError("Invalid period")

    @commands.command()
    async def stats(
            self, ctx,
            moving_average: str = commands.parameter(
                default="no_avg",
                description="Options: weekly_avg, monthly_avg, yearly_avg, no_avg."),
            period: str = commands.parameter(
                default="last_month",
                description="Which data to dosplay. Options: last_week, last_month, last_year, all"),
            user: discord.Member = commands.parameter(
                default=None,
                description="A mention to a discord user."),
            ):
        """
        Display the weight history graph.

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
                await ctx.send("Invalid moving average. Use 'weekly_avg', 'monthly_avg', or 'yearly_avg'.")
                return
    
            moving_averages = []
            for i in range(len(weights) - moving_avg_period + 1):
                avg = np.mean(weights[i:i + moving_avg_period])
                moving_averages.append(avg)
    
            # Adjust dates to match the moving average data length
            moving_avg_dates = dates[moving_avg_period - 1:]
    
            # Create and save the plot with moving average
            plt.figure(figsize=(10, 6))
            plt.plot(dates, weights, marker='o', color='red', linewidth=3, label='Weight')  # Weight data
            plt.plot(moving_avg_dates, moving_averages, color='white', linewidth=3, label='Moving Average')  # Moving average
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
            plt.legend()
            plt.tight_layout()
    
        else:
            # Create and save the plot without moving average
            plt.figure(figsize=(10, 6))
            plt.plot(dates, weights, marker='o', color='red', linewidth=3)  # Weight data
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
    
        plot_path = os.path.join(self.data_folder, f"{user_id}_plot.png")
        plt.savefig(plot_path, transparent=True)
        plt.close()
    
        # Send the plot as an embedded image
        with open(plot_path, "rb") as plot_file:
            plot_data = plot_file.read()
        plot_embed = discord.Embed(title=f"Weight Record for {user.display_name}")
        plot_embed.set_image(url="attachment://plot.png")
        await ctx.send(file=discord.File(plot_path, "plot.png"))



    @commands.command()
    async def remove_weight(self, ctx, date: str, user: discord.Member = None):
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
        user_id = str(user.id)
        file_path = os.path.join(self.data_folder, f"{user_id}.csv")
        temp_file_path = os.path.join(self.data_folder, f"{user_id}_temp.csv")

        if not os.path.exists(file_path):
            await ctx.send("No weight data found for this user.")
            return

        removed = False
        with open(file_path, "r") as input_file, open(temp_file_path, "w", newline="") as output_file:
            csv_reader = csv.reader(input_file)
            csv_writer = csv.writer(output_file)

            # Write header row
            #csv_writer.writerow(["Date", "Weight"])

            for row in csv_reader:
                if row[0] == date:
                    await ctx.send(f"Weight record for {row[0]} ({row[1]} kg) removed.")
                    removed = True
                else:
                    csv_writer.writerow(row)

        os.replace(temp_file_path, file_path)
        if not removed:
            await ctx.send(f"No weight record found for the date {date}.")


    @commands.command()
    async def export(self, ctx, user: discord.Member = None):
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
                file=discord.File(csv_file, filename=f"{user.display_name}_weight_data.csv")
            )

async def setup(bot: commands.Bot):
    """Setup function to add the ConversionCog cog to the bot.

    Args:
        bot (commands.Bot): The bot instance.

    """
    await bot.add_cog(WeightCog(bot))
