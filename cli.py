import json
import datetime
import os

import internal.rooting_tools as rooting_tools
import internal.recording as recording
import internal.homeassistant as hassio


config_file = open("config.json")
config_data = json.load(config_file)
config_file.close()


class CLI:
    def __init__(self, args: list):
        if "adb_path" in config_data.keys():
            self.adb_path = config_data["adb_path"]
        else:
            self.adb_path = "adb"
        if "adb_path" in config_data.keys():
            self.fastboot_path = config_data["fastboot_path"]
        else:
            self.fastboot_path = "fastboot"

        self.version = "1.0.0"  # I'm sure there's a better way to do this
        self.log_info(f"Version: {self.version}")
        self.init_arguments(args)

    def log_info(self, msg: str):
        current_time = datetime.datetime.now().time()
        formatted_time = current_time.strftime("%H:%M:%S")
        print(f"[{formatted_time}] \033[94mINFO:\x1b[0m", msg)

    def log_warn(self, msg: str):
        current_time = datetime.datetime.now().time()
        formatted_time = current_time.strftime("%H:%M:%S")
        print(f"[{formatted_time}] \033[93mWARN:\x1b[0m", msg)

    def log_fail(self, msg: str):
        current_time = datetime.datetime.now().time()
        formatted_time = current_time.strftime("%H:%M:%S")
        print(f"[{formatted_time}] \033[91mFAIL:\x1b[0m", msg)

    def log_success(self, msg: str):
        current_time = datetime.datetime.now().time()
        formatted_time = current_time.strftime("%H:%M:%S")
        print(f"[{formatted_time}] \033[92mSUCCESS:\x1b[0m", msg)

    def init_arguments(self, args: list):
        if "-h" in args or "--help" in args:
            self.print_help()
            exit(0)
        else:
            self.main()

    def print_help(self):
        print(
            "Welcome to echo_cli! This is an interactive shell for the Amazon Echo biscuit_puffin (echo dot 2nd generation)"
        )
        print("For documentation, please visit https://dragon863.github.io/blog/")
        print("Usage:")
        print("  echo_cli.py")
        print("To set ADB path, please edit config.json")

    def main(self):
        while True:
            print()
            options = [
                "Rooting or restore device",
                "Setup recorder",
                "Start or restart process",
                "Setup home assistant indicator",
                "Exit",
            ]
            for index, option in enumerate(options):
                print(
                    f"\033[36m{str(index+1)}:\x1b[0m {option}"
                )  # Please excuse the horrible formatting!
            print()
            option = str(input("\033[36mSelect an option:\x1b[0m > "))
            if (
                option.isdigit()
                and not int(option) > len(options)
                and not int(option) < 1
            ):
                option = int(option)
                if option == 1:
                    rooting_tools.root_menu(self)
                elif option == 2:
                    recording.setup_recorder(self)
                elif option == 3:
                    subOption = input(
                        "Start recorder or home assistant status led? [r/s]"
                    )
                    if subOption.lower() == "r":
                        os.system(
                            f'{self.adb_path} shell "/data/local/tmp/busybox nohup sh /data/local/tmp/spy.sh &>/dev/null &"'
                        )
                        self.log_success(
                            "Started spy script. Please ensure internal/spyserver.py is also active"
                        )
                    else:
                        os.system(
                            f'{self.adb_path} shell "/data/local/tmp/busybox nohup sh /data/local/tmp/led.sh &>/dev/null &"'
                        )
                        self.log_success(
                            "Started home assistant indicator. Please ensure internal/homeassistant.py is also active"
                        )

                elif option == 4:
                    hassio.setup_hassio(self)
                elif option == 5:
                    exit()
            else:
                for index, option in enumerate(options):
                    print(f"\033[36m{str(index+1)}:\x1b[0m {option}")
                self.log_fail(
                    f"Invalid option: {option}. Please ensure option is an integer."
                )
