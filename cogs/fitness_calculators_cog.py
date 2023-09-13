import re
import discord
from discord.ext import commands
from typing import List, Final, Dict

class FitnessCalculatorsCog(commands.Cog):
     # TODO: Issue-10 Extract conversion logic to a library
    # Mapping that defines regular expressions to extract the metrics
    ACTIVITY_KEYWORDS : Final[List[str]] = ['cutting', 'bulking', 'maintaining']
    GENDER_KEYWORDS : Final[List[str]] = ['male', 'female', 'gal', 'guy']
    METRIC_MAPPING : Dict[str, re.Pattern] = {
            "height": re.compile(r'(\d+(\.\d+)?)\s*cm', re.IGNORECASE),
            "weight": re.compile(r'(\d+(\.\d+)?)\s*kg', re.IGNORECASE),
            "bf": re.compile(r'(\d+(\.\d+)?)\s*bf', re.IGNORECASE),
            "gender": re.compile('|'.join(GENDER_KEYWORDS), re.IGNORECASE),
            "age": re.compile(r'(\d+)\s*(?:years?|yo)', re.IGNORECASE),
            "activity": re.compile('|'.join(ACTIVITY_KEYWORDS), re.IGNORECASE)
        }
    REPEATING_GROUPS = {"weight", "bodyfat", "age"}

    def __init__(self, bot : commands.Bot):
        self.bot : commands.Bot = bot
        
        # This stores potentially repeatable data that doesn't need unique calculations
        self.STAT_PIPE_LINE = [
            self.extract_bmi,
            self.extract_ffmi,
            self.extract_tdee
        ]

    @commands.command()
    async def calculators(self, ctx : commands.Context) -> None:
        await ctx.send(("To use the calculators simply type some numbers in a message "
                        "and the bot will figure out what to calculate. "
                        "\n\n"
                        "Examples:\n"
                        "```I'm 193cm and 100kg (This calculates BMI)\n"
                        "196cm and 110kg, 20% bodyfat (calculates FFMI and BMI)```"
                        "\n"
                        "The following data can be specified:\n"
                        "```Height, weight, bodyfat, gender, age, activity level```"
                        ))

    def extract_metrics(self, message_content : str):
        """
        Extracts fitness data required to calculate metrics.
        """
        metric_data : Dict[str, Any] = {
            "height": None,
            "weight": None,
            "bodyfat": None, 
            "gender": None, 
            "age": None, 
            "activity": None
        }
        content_lowercase = message_content.lowered()
        for metric, regex in FitnessCalculatorCog.METRIC_MAPPING.items():
            metric_match = regex.search(content_lowercase)
            if match:
                if metric == "height":
                    height_in_cm = float(match.group(1)) / 100
                    metric_data[metric] = height_in_cm
                elif metric in FitnessCalculatorCog.REPEATING_GROUPS:
                    metric_data[metric] = float(match.group(1))
                else:
                    metric_data[metric] = float(match.group())

        return metric_data

    """
    Extracts BMI with the assumption that `statistics` only consists of filled variables
    """
    def extract_bmi(self, metric_data, statistics):
        can_get_bmi : bool = {"height", "weight"} in statistics
        if can_get_bmi:
            statistics["bmi"] = filled_variables["weight"] / (filled_variables["height"] ** 2)
        
        return statistics

    """
    Extracts FFMI with the assumption that `statistics` only consists of filled variables
    """
    def extract_ffmi(self, metric_data, statistics):
        can_get_ffmi : bool = {"height", "weight", "bodyfat"} in statistics
        if can_get_ffmi:
            total_body_fat : float = weight * (bodyfat / 100)
            lean_weight : float = weight - total_body_fat
            statistics["ffmi"] = round((lean_weight / ((height /100) ** 2) + 6.1 * (1.8 - height / 100) ) / 10000,1)

        return statistics

    """
    Extracts TDEE with the assumption that `statistics` only consists of filled variables
    """
    def extract_tdee(self, metric_data, statistics):
        can_get_tdee : bool = {"height", "weight", "gender", "activity"} in statistics
        if can_get_tdee:
            initial_tdee = 10 * weight + 6.25 * height - 5 * age
            activity_lowercase = activity.lower()
            statistics["tdee"] = initial_tdee
            if activity_lowercase == 'cutting':
                statistics["tdee"] = initial_tdee - 161
            elif activity_lowercase == 'bulking':
                statistics["tdee"] = initial_tdee + 5
        
        return statistics

    # TODO: Issue-10 Put statistic extraction logic into the library
    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        metric_data = self.extract_metrics(message.content)

        # Check if two or more variables are filled
        filled_metrics = [var for metric_name, value in metric_data.items() if value is not None]
        if len(filled_metrics < 2):
            return

        # Calculate statistics
        statistics = {"bmi": None, "ffmi": None, "tdee": None}
        response : str = ""

        for stat_func in self.STAT_PIPELINE:
            statistics = stat_func(metric_data, statistics)

        # Create a response message with the calculated statistics
        response : str = ""
        for stat_name, stat_val in statistics.items():
            response += f"{stat_name}: {stat_val:.2f}\n"

        await message.channel.send(response)

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(FitnessCalculatorsCog(bot))
