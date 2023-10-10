import os
import csv
from datetime import date, datetime, timedelta
import bot_utils as utils
from pathlib import Path
from typing import List, Final

class WeightRepository:
    """
    A weight repository that supports CRUD operations for user weight records
    """

    HEADER_ROW: Final[List[str]] = ["Date", "Weight"]
    """
    Header row of a user weight csv file.
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

    TIMEZONE: Final[datetime.timezone] = datetime.timezone.utc
    """
    The timezone to use when backing up data.
    """

    BACKUP_TIME: Final[datetime.time] = datetime.time(hour=14, minute=8, tzinfo=TIMEZONE)
    """
    The hour and minute to backup the data on.
    """

    def init(self):
        self.config = utils.get_config()
        self.WEIGHT_DATA_PATH: Final[str] = self.config["data-folder"]
        self.can_backup : bool = self.is_git_installed()

    def read_weight_data(self, user_weight_path: str, period):
        """
        Reads all of the user weight data relevant inside a period

        Args:
            user_weight_path (str): The path to the user's weight data.
            period (): The period to read the weight data inside of (e.g. week, month, year).

        Returns the user's weight data from a period
        """

        user_weight_data_from_period = []
        with open(user_weight_path, "r") as csvfile:
            csv_reader: csv.reader = csv.reader(csvfile)
            # Skips the header row
            next(csv_reader)
            for row in csv_reader:
                if row == self.HEADER_ROW:
                    continue
                date: datetime = datetime.strptime(row[0], "%Y-%m-%d").date()
                if self.date_inside_period(period, date):
                    weight = float(row[1])
                    user_weight_data_from_period.append((date, weight))

        return user_weight_data_from_period

    def remove_weight_record(
        self, user_weights_path: str, temp_user_weights_path: str, date: date
    ) -> bool:
        """
        Removes the weight record for a user on a specific date.

        Args:
            user_weights_path (str): Path for a user's weight data.
            temp_user_weights_path (str): Temporary path for a user's weight data. We then use this
                                          to replace the original weight path.
            date (date): The date of the weight record to remove.

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

    def backup_weight_data():
        datetime_now: datetime.datetime = datetime.datetime.now()
        current_date: str = datetime_now.strftime("%Y-%m-%d")
        current_time: str = datetime_now.strftime("%H-%M-%S")

        commit_msg: str = f"(UTC: {current_date} {current_time}) Committing user data"

        # Gets the current working directory of the subprocess/bot instance NOT the working
        # directory of the root process
        working_dir = os.getcwd()
        try:
            # Changes the current directory to the data folder if possible
            os.chdir(self.WEIGHT_DATA_PATH)
        except FileNotFoundError:
            print(f"Git could not find the data folder {self.WEIGHT_DATA_PATH}.")

        self.commit_to_git(commit_msg)
        # Exits out of the BSF-bot-data directory back into BSF-bot
        os.chdir(working_dir)

    def commit_to_git(self, commit_msg: str) -> None:
        """
        Runs the console commands to add, commit and push to Git.

        Args:
            commit_msg (str): The message of the commit message.
        """

        # Ensure that the repo is up to date first
        subprocess.run(["git", "fetch"])
        subprocess.run(["git", "checkout", "origin/master"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", commit_msg])
        subprocess.run(["git", "push", "origin", "HEAD:master"])

    # TODO: I believe this function hasn't actually been tested by anybody
    # to see if it works
    def is_git_installed(self) -> bool:
        """
        Checks if git is installed by checking the version.

        Returns a boolean result based on if git is installed or not.
        """

        try:
            subprocess.run(
                ["git", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
        except subprocess.CalledProcessError as e:
            # TODO: Do we use logging instead?
            if e.returncode == 127:
                print(
                    "ERROR: Git isn't installed. Please install Git on the host or ensure the PATH"
                    " variable has been set properly."
                )
            else:
                print(f"ERROR: Unknown. Return code: {e.returncode}")
                print(f"Standard output: {e.stdout}")
                print(f"Standard error: {e.stderr}")

            return False
        return True

    def date_inside_period(self, period: str, date: date) -> bool:
        """
        Check if a date is inside of a period.

        Args:
            period (str): The moving average period specified.
            date (str): The date being checked to see if it is in a period.

        Returns True if date is inside a period.
        """

        today = datetime.now().date()

        if period == "all":
            return True

        try:
            days = self.MOVING_AVG_PERIODS[period]
            time_delta: timedelta = timedelta(days)
        except ValueError:
            raise ValueError(f"Invalid period: {period}.")

        start = today - time_delta
        return start <= date <= today
