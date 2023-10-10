import sys
sys.path.append(("../../fitness_libs"))

import os
from pathlib import Path
from typing import Final, List
import bot_utils as utils


# TODO: Handle the edge case where the user could inject directories when specifying
# `info_file_name`
class InfoRepository:
    def init(self):
        self.config = utils.get_config()
        self.INFO_COMMANDS_PATH: Final[Path] = Path(self.config["info-commands-path"])
        self.INFO_COMMANDS_PATH.touch()

    def read_info_command(info_command_name: str) -> str | None:
        info_file_path: str = f"{self.INFO_COMMANDS_PATH}/{info_command_name}.txt"
        info_file_found: bool = os.path.isfile(info_file_path)
        if info_file_found:
            with open(info_file_path, "r") as file:
                info_content: str = file.read()
        else:
            return None

        return info_content

    def remove_info_command(info_command_name: str) -> bool:
        """
        Removes an info command based on the `info_command_name` passed in.

        Args:
            info_command_name (str): The name of the info command.

        Returns the boolean result of whether the info command file was found.
        """

        info_file_path: str = f"{self.INFO_COMMANDS_PATH}/{info_command_name}.txt"
        info_file_found: bool = os.path.isfile(info_file_path)
        if info_file_found:
            os.remove(info_file_path)
            return True
        else:
            return False

    def list_commands() -> List[str]:
        """
        List all saved commands in alphabetical order.

        Returns a list of the info command names if any.
        """

        saved_info_files: List[str] = os.listdir(self.INFO_COMMANDS_PATH)
        info_txt_files: List[str] = sorted(
            [file[:-4] for file in saved_info_files if file.endswith(".txt")]
        )

        # TODO: Check if it can handle info_txt_files if there is nothing to join
        # without exception/error
        info_file_list: List[str] = " ".join(info_txt_files)
        return info_txt_files

    def create_info_command(info_command_name: str, info_content: str):
        """
        Creates a new info command.

        Args:
            info_command_name (str): The name of the new info command.
            info_content (str): The contents of the new info command.
        """

        info_file_path: str = f"{self.INFO_COMMANDS_PATH}/{info_command_name}.txt"
        with open(info_file_path, "w") as file:
            file.write(info_content)
