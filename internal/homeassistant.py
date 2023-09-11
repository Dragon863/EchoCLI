import os


def handle(process, cli):
    if process == 0:
        pass
    else:
        cli.log_fail("Command failed. Exiting...")
        exit("Command fail")


def setup_hassio(cli):
    cli.log_info(
        "Please edit the URL in the file shell/led.sh to your home assistant instance. Press enter to proceed..."
    )  # TODO: Pull from config file

    input("> ")

    cli.log_info("Waiting for booted device to be connected...")
    os.system(f"{cli.adb_path} wait-for-device")
    cli.log_info("Booted device connected. Pushing home assistant shell script...")
    push_led = os.system(f"{cli.adb_path} push shell/led.sh /data/local/tmp")
    handle(push_led, cli)
    push_curl = os.system(f"{cli.adb_path} push shell/curl /data/local/tmp")
    handle(push_curl, cli)
    chmod_curl = os.system(f"{cli.adb_path} shell toybox chmod +x /data/local/tmp/curl")
    handle(chmod_curl, cli)
    push_busybox = os.system(f"{cli.adb_path} push shell/busybox /data/local/tmp")
    handle(push_busybox, cli)
    chmod_busybox = os.system(f"{cli.adb_path} shell toybox chmod +x /data/local/tmp/busybox")
    handle(chmod_busybox, cli)

    cli.log_success(
        "Home assistant shell script, busybox and curl static binary pushed to device."
    )

    cli.log_info("Starting processes...")
    os.system(
        f'{cli.adb_path} shell "/data/local/tmp/busybox nohup sh /data/local/tmp/led.sh &>/dev/null &"'
    )
    cli.log_success("Started process!")
    return
