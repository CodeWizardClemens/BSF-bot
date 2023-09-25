#!/usr/bin/env python3

from typing import Dict, Optional

from discord.ext import commands

goal_dict: Dict[int, str] = {
    1: "Bulk",
    2: "Cut",
    3: "Maintain",
}

bodyfat_dict: Dict[int, Optional[int]] = {
    1: 30,
    2: 25,
    3: 20,
    4: 15,
    5: 10,
    6: None,
}

gender_dict: Dict[int, str] = {
    1: "Male",
    2: "Female",
}

activity_dict: Dict[int, float] = {
    1: 1.2,
    2: 1.375,
    3: 1.55,
    4: 1.725,
    5: 1.9,
}

diet_goal_kcals_conversion: Dict[str, int] = {
    "Bulk": 200,
    "Cut": -500,
    "Maintain": 0,
}

goal_protein_multiplier: Dict[str, float] = {
    "Bulk": 1.6,
    "Cut": 2,
    "Maintain": 1.8,
}


def calculate_state_weight_martin_gerkhan(height):
    """Martin Berkhan formuila's with variable height"""

    # https://leangains.com/maximum-muscular-potential-of-drug-free-athletes-updated-dec-31st/
    r = 0.1 * (height - 190) + 101
    return height - r


def get_max_weight(ffmi, cm, bf):
    lean_kg = (ffmi - (6.1 * (1.8 - cm * 0.01))) * pow(cm * 0.01, 2)
    kg = lean_kg + lean_kg * bf / 100
    return kg


def calculate_muscle_left_to_build(cm, bf, kg):
    lean_kg_max = (25 - (6.1 * (1.8 - cm * 0.01))) * pow(cm * 0.01, 2)
    lean_kg_now = kg * (100 - bf) * 0.01
    return lean_kg_max - lean_kg_now


def calculate_years_left_to_build_muscle(kg):
    gain_rate = [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 5.5, 11, 22.5]
    years = 0
    for gain in gain_rate:
        if kg <= 0:
            break
        years += 1
        kg = kg - gain
    return years


def calculate_ffm(weight, bodyfat):
    return weight * (1 - (bodyfat / 100))


def calculate_total_bodyfat(weight, bodyfat):
    return weight - calculate_ffm(weight, bodyfat)


def calculate_ffmi(weight, height, bodyfat):
    return calculate_ffm(weight, bodyfat) / pow(height / 100, 2)


def calculate_adjusted_ffmi(weight, height, bodyfat):
    return calculate_ffmi(weight, height, bodyfat) + 6.1 * (1.8 - (height / 100))


def calculate_protein(bodyweight, goal, bodyfat):
    bodyfat_multiplier = 0

    if bodyweight is None or goal is None or bodyfat is None:
        raise TypeError

    if bodyfat <= 10:
        bodyfat_multiplier = 1.2
    elif bodyfat >= 25:
        bodyfat_multiplier = 0.8
    else:
        bodyfat_multiplier = 1

    return round(bodyweight * goal_protein_multiplier[goal] * bodyfat_multiplier)


def calculate_fats(kcals):
    if kcals is None:
        raise TypeError
    return round(kcals * 0.2 / 9)


def calculate_carbs(kcals, fats, protein):
    if kcals is None or fats is None or protein is None:
        raise TypeError
    return round((kcals - fats * 9 - protein * 4) / 4)


def calculate_tdee(bmr, multiplier):
    if bmr is None or multiplier is None:
        raise TypeError
    return round(bmr * multiplier)


def calculate_bmi(bodyweight, height):
    if bodyweight is None or height is None:
        raise TypeError
    return round(bodyweight / pow((height / 100), 2))


def calculate_bmr(bodyweight, height, age, gender):
    if bodyweight is None or height is None or age is None or gender is None:
        raise TypeError

    if gender == "Male":
        return round((13.397 * bodyweight) + (4.799 * height) - (5.677 * age) + 88.362)
    return round((9.247 * bodyweight) + (3.098 * height) - (4.330 * age) + 447.593)


class MealplanCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.goal = None
        self.bodyfat = None
        self.kcals = None
        self.bodyweight = None
        self.macros = {"protein": None, "fats": None, "carbs": None}
        self.age = None
        self.height = None
        self.activity_level = None
        self.last_msg = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("Module: Mealplan")

    @commands.command(brief="Show the last created mealplan")
    async def last_macros(self, ctx):
        if self.last_msg:
            await ctx.send("*You can create a meal plan by running*: **BSF mealplan**")
            await ctx.send(self.last_msg)
            return
        await ctx.send("*You can create a meal plan by running*: **BSF mealplan**")

    @commands.command(brief="Create a meal plan")
    async def mealplan(self, ctx):
        await ctx.send(
            "__**Disclaimer/Introduction**__\n"
            "Hi! I will help you give some personallised nutrition recommendations "
            "based on some questions I'm going to ask you. Be mindful that I'm just "
            "a tool and not a certified proffesional. My recommendations are oversimplified "
            "and don't compare to a trained human being's advice.\n"
        )
        await self.ask_goal(ctx)
        await self.ask_bodyfat(ctx)
        await self.ask_gender(ctx)
        await self.ask_weight(ctx)
        await self.ask_kcals(ctx)
        await self.ask_height(ctx)
        await self.ask_age(ctx)

        if not self.kcals:
            await self.ask_activity_level(ctx)
            tdee = calculate_tdee(
                calculate_bmr(self.bodyweight, self.height, self.age, self.gender),
                self.activity_level,
            )
            self.kcals = tdee + diet_goal_kcals_conversion[self.goal]

        self.macros["protein"] = calculate_protein(self.bodyweight, self.goal, self.bodyfat)
        self.macros["fats"] = calculate_fats(self.kcals)
        self.macros["carbs"] = calculate_carbs(
            self.kcals, self.macros["fats"], self.macros["protein"]
        )

        self.muscle_left_to_build = calculate_muscle_left_to_build(
            self.height, self.bodyfat, self.bodyweight
        )
        self.years_to_build_muscle = calculate_years_left_to_build_muscle(self.muscle_left_to_build)

        self.last_msg = (
            f"__**This is a summary of your general diet recommendations**__\n"
            "```"
            f"kcals: {self.kcals}\n"
            f"Protein: {self.macros['protein']}\n"
            f"Fats: {self.macros['fats']}\n"
            f"Carbs: {self.macros['carbs']}\n"
            "```"
            # "Start with the macros listed above following macros. Be mindfull that this is just "
            # "an estemation. "
            # f"{await self.get_adjustment_string_based_on_goal()}"
            f"\n"
            f"__**Body Stats**__\n"
            f"```"
            f"BMI: {calculate_bmi(self.bodyweight, self.height)}\n"
            "FFMI:"
            f"{round(calculate_adjusted_ffmi(self.bodyweight, self.height, self.bodyfat),1)}\n"
            "Total fat mass (kg):"
            f"{round(calculate_total_bodyfat(self.bodyweight, self.bodyfat))}\n"
            f"Total lean mass (kg): {round(calculate_ffm(self.bodyweight, self.bodyfat))}\n"
            f"```"
            f"\n"
            f"__**Future Body Stats**__\n"
            f"```"
            f"You have about {round(self.muscle_left_to_build)}"
            f" kg of muscle left to build in your training. This will take about "
            f"{round(self.years_to_build_muscle)} years to build."
            f"```"
        )

        await ctx.send(self.last_msg)

        # if (await self.ask_continue_meal_plan(ctx) == True):
        #    await ask_amount_of_meals(ctx)

    async def get_adjustment_string_based_on_goal(self):
        if self.goal == "Maintain":
            return (
                "You will need to track you weight to make sure you are maintaining it. "
                f"If you gain about 1kg per month lower the carbs to {self.macros['carbs']-50}. "
                f"If you lose about 1kg per month up the carbs to {self.macros['carbs']+50}. "
            )
        elif self.goal == "Bulk":
            return (
                "You will need to track your weight to make sure you are gaining "
                "About 1kg per month. If this is not the case. Bump up the carbs to about "
                f"{self.macros['carbs']+50} to {self.macros['carbs']+75} grams."
            )
        elif self.goal == "Cut":
            return (
                "You will need to track you weight to make sure you are lowing weight on average "
                "If you are not losing 0.5kg per week on average you need to drop the carbs by "
                f"{self.macros['carbs']-50} to {self.macros['carbs']-75} grams per day."
            )

    async def ask_kcals(self, ctx):
        await ctx.send(
            "__**Do you know how many kcals you need?**__\n" "1) No help me through it\n" "2) Yes\n"
        )
        while True:

            def check(msg):
                return msg.channel == ctx.channel

            msg = await self.client.wait_for("message", check=check)

            valid_kcal_inputs = msg.content.isnumeric() and 1 <= int(msg.content) <= 2
            if valid_kcal_inputs:
                break
            else:
                await ctx.send("Pick number 1 or 2")

        if int(msg.content) == 1:
            return
        await self.ask_specific_kcals(ctx)

    async def ask_continue_meal_plan(self, ctx):
        await ctx.send(
            "Do you want to continue with making a meal plan?\n"
            "1) No, that's all I need.\n"
            "2) Yes, help me out.\n"
        )
        while True:

            def check(msg):
                return msg.channel == ctx.channel

            msg = await self.client.wait_for("message", check=check)

            valid_mealplan_inputs = msg.content.isnumeric() and 1 <= int(msg.content) <= 2
            if valid_mealplan_inputs:
                if int(msg.content) == 1:
                    return False
                return True
            else:
                await ctx.send("Pick number 1 or 2")

        if int(msg.content) == 1:
            await ctx.send("Goodbye!")
        else:
            await ctx.send("Sorry, that feature is coming in the future! :)")

    async def ask_specific_kcals(self, ctx):
        await ctx.send("How many kcals do you need in a day?")

        while True:

            def check(msg):
                return msg.channel == ctx.channel

            msg = await self.client.wait_for("message", check=check)

            valid_kcal_needs = msg.content.isnumeric() and 1000 <= int(msg.content) <= 10000
            if valid_kcal_needs:
                self.kcals = int(msg.content)
                print(f"kcals: {self.kcals}")
                break
            else:
                await ctx.send("Must be between 1000 and 10000")

    async def ask_height(self, ctx):
        await ctx.send("How tall are you in cm?")

        while True:

            def check(msg):
                return msg.channel == ctx.channel

            msg = await self.client.wait_for("message", check=check)

            valid_height_cm = msg.content.isnumeric() and 140 <= int(msg.content) <= 250
            if valid_height_cm:
                self.height = int(msg.content)
                print(f"height: {self.height}")
                break
            else:
                await ctx.send("Must be a number without cm at the end, between 140 and 250.")

    async def ask_age(self, ctx):
        await ctx.send("How old are you?")

        while True:

            def check(msg):
                return msg.channel == ctx.channel

            msg = await self.client.wait_for("message", check=check)

            valid_age = msg.content.isnumeric() and 18 <= int(msg.content) <= 85
            if valid_age:
                self.age = int(msg.content)
                print(f"age: {self.age}")
                break
            else:
                await ctx.send("Age must be between 18 and 85.")

    async def ask_bodyfat(self, ctx):
        await ctx.send(
            "__**If you had to describe your bodyfat. Which best describes your body?**__\n"
            "1) I have a lot of excess body fat (30%)\n"
            "2) I have some excess body fat (25%)\n"
            "3) I have some body fat, but not an unhealthy amount (20%)\n"
            "4) I am decently lean, and don't have much bodyfat (15%)\n"
            "5) I am very lean for the average person (10%)\n"
            "6) I want to manually fill in my bodyfat\n"
        )
        while True:

            def check_same_channel(msg):
                return msg.channel == ctx.channel

            msg = await self.client.wait_for("message", check=check_same_channel)

            valid_bodyfat = msg.content.isnumeric() and 1 <= int(msg.content) <= 6
            if valid_bodyfat:
                self.bodyfat = bodyfat_dict[int(msg.content)]
                print(f"bodyfat: {self.bodyfat}")
                break
            else:
                await ctx.send("Please enter a number 1 and 6.")

        if not self.bodyfat:
            await self.ask_bodyfat_specific_number(ctx)

    async def ask_bodyfat_specific_number(self, ctx):
        await ctx.send("What is your bodyfat percentage? Only type the number.")

        while True:

            def check_same_channel(msg):
                return msg.channel == ctx.channel

            msg = await self.client.wait_for("message", check=check_same_channel)

            valid_bf_value = msg.content.isnumeric() and 3 <= int(msg.content) <= 50
            if valid_bf_value:
                self.bodyfat = int(msg.content)
                print(f"bodyfat: {self.bodyfat}")
                break
            else:
                await ctx.send("Please enter a number between 3 and 60")

    async def ask_weight(self, ctx):
        await ctx.send("How much do you weigh (in kg)?")

        while True:

            def check_same_channel(msg):
                return msg.channel == ctx.channel

            msg = await self.client.wait_for("message", check=check_same_channel)

            valid_weight = msg.content.isnumeric() and 30 <= int(msg.content) <= 300
            if valid_weight:
                self.bodyweight = int(msg.content)
                print(f"bodyweight: {self.bodyweight}")
                break
            else:
                await ctx.send("Please enter a number between 30 and 300 without kg at the end.")

    async def ask_gender(self, ctx):
        await ctx.send("What is your gender? \n" "* Male\n" "* Female\n")
        while True:

            def check_same_channel(msg):
                return msg.channel == ctx.channel

            msg = await self.client.wait_for("message", check=check_same_channel)

            lowercase_content = msg.content.lower()
            if lowercase_content == "male" or lowercase_content == "female":
                self.gender = msg.content
                print(f"gender: {self.gender}")
                break
            else:
                await ctx.send("Please type male or female")

    async def ask_goal(self, ctx):
        await ctx.send(
            "__**Which of the follow numbers desribes your current goal the best?**__\n"
            "1) Gaining bodyweight / Gaining muscle\n"
            "2) Losing body fat\n"
            "3) Maintaining my bodyweight while gaining muscle and losing fat\n"
        )
        while True:

            def check_same_channel(msg):
                return msg.channel == ctx.channel

            msg = await self.client.wait_for("message", check=check_same_channel)

            valid_goal_input: bool = msg.content.isnumeric() and 1 <= int(msg.content) <= 3
            if valid_goal_input:
                self.goal = goal_dict[int(msg.content)]
                print(f"goal: {self.goal}")
                break
            else:
                await ctx.send("Please give a valid response between 1 and 3")

    async def ask_activity_level(self, ctx):
        await ctx.send(
            "__**How active are you planing to be on your diet?**__\n"
            "1) Sedentary. With little to no excercise\n"
            "2) Light exercise. 1 to 3  times per week\n"
            "3) Moderately active. 3-5 times per week\n"
            "4) heavy cardio intensive exercise. 6-7x a week\n"
            "5) Very heavy exercise. Twice per day, Or active day job"
        )
        while True:

            def check_same_channel(msg):
                return msg.channel == ctx.channel

            msg = await self.client.wait_for("message", check=check_same_channel)

            valid_activity_level: bool = msg.content.isnumeric() and 1 <= int(msg.content) <= 5
            if valid_activity_level:
                self.activity_level = activity_dict[int(msg.content)]
                print(f"activity_level: {self.activity_level}")
                break
            else:
                await ctx.send("Please give a valid response between 1 and 5")


async def setup(client):
    await client.add_cog(MealplanCog(client))


if __name__ == "__main__":
    breakpoint()
