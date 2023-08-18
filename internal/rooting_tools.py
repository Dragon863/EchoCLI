import os
import sys
from .fos_flags import calculate_fos_flags


def root_menu(cli):
    print()
    options = ["Root or restore", "Calculate and set fos_flags", "Exit"]
    for index, option in enumerate(options):
        print(f"\033[36m{str(index+1)}:\x1b[0m {option}")
    print()
    while True:
        option = str(input("\033[36mSelect an option:\x1b[0m > "))
        if option.isdigit() and not int(option) > len(options) and not int(option) < 1:
            if option == "1":
                root(cli)
            elif option == "2":
                cli.log_info(
                    "Please only use this option once you have run the rooting process. Press Ctrl+C if you wish to cancel"
                )
                fos_flag_value = calculate_fos_flags()
                cli.log_info(f"Setting fos_flags to {fos_flag_value} using fastboot...")
                cli.log_info(
                    "Please replug your device now and run the mtkclient command in the README in another terminal whilst holding the uber (dot) button. When you see a green LED ring, press enter to continue..."
                )
                input("[Waiting for enter press...] > ")
                try:
                    os.system(f"{cli.fastboot_path} oem flags {str(fos_flag_value)}")
                    cli.log_success("Successfully set fos_flags, your device is now rooted! Your echo will shut down, and you will be able to boot it using the mtkclient command in the README")
                    os.system(f"{cli.fastboot_path} reboot")
                    return
                except Exception as e:
                    cli.log_fail(f"Failed to set fos_flags: {e}")
            elif option == "3":
                return

        else:
            for index, option in enumerate(options):
                print(f"\033[36m{str(index+1)}:\x1b[0m {option}")
            cli.log_fail(
                f"Invalid option: {option}. Please ensure option is an integer."
            )


def root(cli):
    cli.log_info(
        "Please short the device as shown in the image at https://dragon863.github.io/blog/mainboard.jpg"
    )
    cli.log_info("To open the device, you will need a torx 8 screwdriver.")
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/amonet")
    os.system(f"{sys.executable} -m amonet")
