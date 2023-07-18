def calculate_fos_flags():
    options = {
        "Turn ADB debugging on": 0x1,
        "ADB debugging as root": 0x2,
        "Enable UART output after lk": 0x4,
        "Increase log level": 0x8,
        "Enable ramdump": 0x10,
        "Disable ADB Authorization": 0x20,
        "Enable DM verity": 0x40,
        "Disable DM verity": 0x80,
        "Disable boot dex optimising": 0x100,
    }

    total = 0
    recommended = input("\033[91mDo you want to use recommended options? (y/n) > ")
    if recommended.lower() == "y":
        total = 0x1+0x2+0x20+0x80 # Standard options
    else:
        print("Please select which features you want to enable.")
        print()
        for option, value in options.items():
            while True:
                user_input = input(f"Do you want to enable '{option}'? (y/n): ")
                if user_input.lower() == "y":
                    total |= value
                    break
                elif user_input.lower() == "n":
                    break
                else:
                    print(f"\033[91mFAIL:\x1b[0m Invalid input '{user_input}'")

    return hex(total)
