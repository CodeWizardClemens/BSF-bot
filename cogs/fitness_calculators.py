import re

import discord
from discord.ext import commands


class FitnessCalculators(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activity_keywords = ["cutting", "bulking", "maintaining"]

    @commands.command()
    async def calculators(self, ctx):
        await ctx.send(
            (
                "To use the calculators simply type some numbers in a message "
                "and the bot will figure out what to calculate. "
                "\n\n"
                "Examples:\n"
                "```I'm 193cm and 100kg (This calculates BMI)\n"
                "196cm and 110kg, 20% bodyfat (calculates FFMI and BMI)```"
                "\n"
                "The following data can be specified:\n"
                "```Height, weight, bodyfat, gender, age, activity level```"
            )
        )

    def extract_data(self, message_content):
        # Define regular expressions for each data element
        height_regex = re.compile(r"(\d+(\.\d+)?)\s*cm")
        weight_regex = re.compile(r"(\d+(\.\d+)?)\s*kg")
        bf_regex = re.compile(r"(\d+(\.\d+)?)\s*bf")
        gender_regex = re.compile(r"(male|female|gal|guy)")
        age_regex = re.compile(r"(\d+)\s*(?:years?|yo)")
        activity_regex = re.compile("|".join(self.activity_keywords), re.IGNORECASE)

        # Initialize variables
        height, weight, bodyfat, gender, age, activity = None, None, None, None, None, None

        # Extract data using regular expressions
        if height_match := height_regex.search(message_content):
            height = float(height_match.group(1)) / 100  # Convert cm to meters

        if weight_match := weight_regex.search(message_content):
            weight = float(weight_match.group(1))

        if bf_match := bf_regex.search(message_content):
            bodyfat = float(bf_match.group(1))

        if gender_match := gender_regex.search(message_content.lower()):
            gender = gender_match.group()

        if age_match := age_regex.search(message_content.lower()):
            age = int(age_match.group(1))

        if activity_match := activity_regex.search(message_content.lower()):
            activity = activity_match.group()

        return height, weight, bodyfat, gender, age, activity

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if the message is from a bot or not in a direct message
        # if message.author.bot or not message.guild:
        #    return

        # Extract data from the message
        height, weight, bodyfat, gender, age, activity = self.extract_data(message.content)

        # Check if two or more variables are filled
        filled_variables = [
            var for var in [height, weight, bodyfat, gender, age, activity] if var is not None
        ]
        if len(filled_variables) >= 2:
            # Calculate statistics
            bmi = None
            ffmi = None
            tdee = None

            if height and weight:
                bmi = weight / (height**2)

            if weight and bodyfat and height:
                total_body_fat = weight * (bodyfat / 100)
                lean_weight = weight - total_body_fat
                ffmi = round(
                    (lean_weight / ((height / 100) ** 2) + 6.1 * (1.8 - height / 100)) / 10000, 1
                )

            if height and weight and gender and activity:
                if activity.lower() == "cutting":
                    tdee = 10 * weight + 6.25 * height - 5 * age - 161
                elif activity.lower() == "bulking":
                    tdee = 10 * weight + 6.25 * height - 5 * age + 5
                elif activity.lower() == "maintaining":
                    tdee = 10 * weight + 6.25 * height - 5 * age

            # Create a response message with the extracted data and calculated statistics
            # response = f"Height (cm): {height * 100}, Weight (kg): {weight}, Bodyfat (%): {bodyfat}, Gender: {gender}, Age: {age}, Activity: {activity}\n"
            response = ""
            if bmi is not None:
                response += f"BMI: {bmi:.2f}\n"
            if ffmi is not None:
                response += f"FFMI: {ffmi:.2f}\n"
            if tdee is not None:
                response += f"TDEE: {tdee:.2f}\n"

            await message.channel.send(response)


async def setup(bot):
    await bot.add_cog(FitnessCalculators(bot))
