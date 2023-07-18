import os


def handle(process, cli):
    if process == 0:
        pass
    else:
        cli.log_fail("Command failed. Exiting...")
        exit("Err: command fail")


def setup_recorder(cli):
    cli.log_info(
        "Please edit the IP in the file shell/spy.sh to your local IP. Press enter to proceed..."
    )  # TODO: Pull from config file

    input()

    cli.log_info("Waiting for booted device to be connected...")
    os.system(f"{cli.adb_path} wait-for-device")
    cli.log_info("Booted device connected. Pushing recorder shell script...")

    push_spy = os.system(f"{cli.adb_path} push shell/spy.sh /data/local/tmp")
    handle(push_spy, cli)
    push_curl = os.system(f"{cli.adb_path} push shell/curl /data/local/tmp")
    handle(push_curl, cli)

    chmod_curl = os.system(f"{cli.adb_path} shell toybox chmod +x curl")
    handle(chmod_curl, cli)
    push_busybox = os.system(f"{cli.adb_path} push shell/busybox /data/local/tmp")
    handle(push_busybox, cli)
    chmod_busybox = os.system(f"{cli.adb_path} shell toybox chmod +x busybox")
    handle(chmod_busybox, cli)
    cli.log_success(
        "Recorder shell script, busybox curl static binary pushed to device."
    )

    cli.log_info("Starting processes...")
    os.system(
        f'{cli.adb_path} shell "/data/local/tmp/busybox nohup sh /data/local/tmp/led.sh &>/dev/null &"'
    )
    cli.log_success("Started process!")
    return
