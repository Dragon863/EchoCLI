import struct
import datetime
import hashlib
import shutil
import os

from amonet.common import Device
from amonet.handshake import handshake
from amonet.load_payload import load_payload
from amonet.logger import log


def log_info(msg: str):
    current_time = datetime.datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"[{formatted_time}] \033[94mINFO:\x1b[0m", msg)


def log_warn(msg: str):
    current_time = datetime.datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"[{formatted_time}] \033[93mWARN:\x1b[0m", msg)


def log_fail(msg: str):
    current_time = datetime.datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"[{formatted_time}] \033[91mFAIL:\x1b[0m", msg)


def log_success(msg: str):
    current_time = datetime.datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"[{formatted_time}] \033[92mSUCCESS:\x1b[0m", msg)


def modify_lk(version: str, slot: str):
    if version == "6.5.0.5":
        with open(f"lk_{slot}.bin", "r+b") as file:
            file.seek(0x00001B00)
            file.write(bytes.fromhex("80940200079702000120704700214ff4"))

    else:
        with open(f"lk_{slot}.bin", "r+b") as file:
            file.seek(0x00001B00)
            file.write(bytes.fromhex("489402004f9702000120704700214ff4"))
    return


def switch_boot0(dev):
    dev.emmc_switch(1)
    block = dev.emmc_read(0)
    if block[0:9] != b"EMMC_BOOT" and block[0:9] != b"BADD_BOOT":
        # dev.reboot()
        log_warn("BOOT0 partition may be corrupt")


def flash_data(dev, data, start_block, max_size=0):
    while len(data) % 0x200 != 0:
        data += b"\x00"

    if max_size and len(data) > max_size:
        log_fail("data too big to flash")
        exit()

    blocks = len(data) // 0x200
    for x in range(blocks):
        print("[{} / {}]".format(x + 1, blocks), end="\r")
        dev.emmc_write(start_block + x, data[x * 0x200 : (x + 1) * 0x200])
    print("")


def read_boot0(dev):
    switch_boot0(dev)
    i = 0
    with open("boot0.bin", "wb") as fout:
        while True:
            data = dev.emmc_read(i)
            fout.write(data)
            i = i + 1


#  read data. note: number of bytes is increased to nearest blocksize
def dump_binary(dev, outfile, start_block, nblocks=0):
    try:
        initialBlocks = nblocks
        with open(outfile, "wb") as fout:
            while nblocks > 0:
                data = dev.emmc_read(start_block)
                fout.write(data)
                start_block = start_block + 1
                nblocks = nblocks - 1
                print(str(100 - ((nblocks / initialBlocks) * 100)) + "%", end="\r")
                # print("[{} / {}]".format(nblocks, initialBlocks), end='\r')
        log_success(f"Dumped {outfile} from device.")
    except:
        log_fail(f"Failed to dump {outfile}")


def flash_binary(dev, path, start_block, max_size=0):
    with open(path, "rb") as fin:
        data = fin.read()
    while len(data) % 0x200 != 0:
        data += b"\x00"

    log_info(
        f"Data is {len(data)} and maximum size is {max_size if max_size > 0 else 'not defined'}"
    )
    if max_size and len(data) > max_size:
        log_fail("Data too big to flash")
        exit()

    blocks = len(data) // 0x200
    for x in range(blocks):
        print("[{} / {}]".format(x + 1, blocks), end="\r")
        dev.emmc_write(start_block + x, data[x * 0x200 : (x + 1) * 0x200])
    print()


def switch_user(dev):
    dev.emmc_switch(0)
    block = dev.emmc_read(0)
    if block[510:512] != b"\x55\xAA":
        # print(block[510:512])
        # dev.reboot()
        log_info("There may be a problem with your GPT. It may be safe to ignore this.")


def parse_gpt(dev):
    data = (
        dev.emmc_read(0x400 // 0x200)
        + dev.emmc_read(0x600 // 0x200)
        + dev.emmc_read(0x800 // 0x200)
        + dev.emmc_read(0xA00 // 0x200)
    )
    num = len(data) // 0x80
    parts = dict()
    for x in range(num):
        part = data[x * 0x80 : (x + 1) * 0x80]
        part_name = part[0x38:].decode("utf-16le").rstrip("\x00")
        part_start = struct.unpack("<Q", part[0x20:0x28])[0]
        part_end = struct.unpack("<Q", part[0x28:0x30])[0]
        parts[part_name] = (part_start, part_end - part_start + 1)
        pass
    return parts


def main():
    while True:
        try:
            dev = Device()
            dev.find_device()

            # 0.1) Handshake
            handshake(dev)
        except RuntimeError:
            log("wrong handshake response, probably in preloader")
            continue
        log("handshake success!")
        break

    # 0.2) Load brom payload
    load_payload(dev, "brom-payload/build/payload.bin")

    # 1) Sanity check GPT
    log("Check GPT")
    switch_user(dev)

    # 1.1) Parse gpt
    gpt = parse_gpt(dev)
    print("Partitions:")
    print(gpt)
    print()
    if (
        "lk_a" not in gpt
        or "tee1" not in gpt
        or "boot_a" not in gpt
        or "misc" not in gpt
    ):
        log_warn(
            "There may be an issue with your GPT. If the partitions shown above have readable names, it is safe to continue. Press enter to proceed..."
        )
        input()

    print("Would you like to root your device, or restore it?")
    choice = input("[root/restore] > ")
    if choice.lower() == "restore":
        switch_boot0(dev)
        flash_binary(dev, "backup/preloader.bin", 0)
        log_info("Restored preloader...")
        flash_binary(dev, "misc.bin", gpt["misc"][0])
        log_info("Restored misc partition...")
        switch_user(dev)
        if "lk_a.bin" in os.listdir("backup/"):
            flash_binary(dev, "lk_a.bin", gpt["lk_a"][0])
            log_info("Restored lk_a partition...")
        elif "lk_b.bin" in os.listdir("backup/"):
            flash_binary(dev, "lk_b.bin", gpt["lk_b"][0])
            log_info("Restored lk_b partition...")
        log_success(
            "Restored device! If you experience any problems, please contact me."
        )

    switch_user(dev)
    dump_binary(dev, "misc.bin", gpt["misc"][0], gpt["misc"][1])
    shutil.copyfile("misc.bin", "backup/misc.bin")
    log_info("Backed up misc partition...")
    switch_boot0(dev)
    log_info(
        """
        This next step WILL brick your preloader, rendering your device unbootable without a computer, as this is a TETHERED exploit. This is a reversible change. Press enter if you understand the consequences and accept that I am not responsible for any damage to you device...
        """
    )
    input()
    dump_binary(dev, "backup/preloader.bin", 0, 1024)
    log_info("Backed up preloader...")
    log_info("Clearing preloader header")
    flash_data(
        dev, b"EMMC_BOOT" + b"\x00" * ((0x200 * 8) - 9), 0
    )  # Thanks to chaosmaster for this useful snippet
    dump_binary(dev, "../../preloader_no_hdr.bin", 0, 1024)
    switch_user(dev)

    nonzero = []
    with open("misc.bin", "r+b") as file:
        data = file.read(1)
        while data:
            data = file.read(1)
            if data != b"\x00":
                nonzero.append(data)
    if (
        data[3] > data[4]
    ):  # Check 0x363 in a hex editor, it determines the A/B slots Thanks @j10hx40r !
        log_info("Detected that device is using slot A.")
        slot = "a"
    else:
        log_info("Detected that device is using slot B.")
        slot = "b"

    dump_binary(dev, f"lk_{slot}", gpt[f"lk_{slot}.bin"][0])
    shutil.copyfile(f"lk_{slot}.bin", f"backup/lk_{slot}.bin")
    log_info(f"Backed up LK {slot} partition...")
    """
    Calculate md5 hash of lk to determine version. We do this to avoid copyright issues; by doing this we don't need the copyrighted files, we can 
    pull them from the device and modify them.
    """
    with open(f"lk_{slot}.bin", "rb") as f:
        hash = hashlib.md5()
        while chunk := f.read(8192):
            hash.update(chunk)

    if hash.hexdigest().lower() == "f43bcd1e4ea0bb1fec68da10cc8109fb":
        log_info("Detected lk version 6.5.0.5")
        version = "6.5.0.5"
    elif hash.hexdigest().lower() == "54e0629919dc284552215ca084f7834f":
        log_info("Detected lk version 6.5.5.9")
        version = "6.5.5.9"
    else:
        log_warn(
            """
                Could not detect LK version. Try updating your device using an OTA, or the official app if this method has not yet been patched. Press enter to continue, or press Ctrl+C to abort (safer).
                """
        )
        input()
    modify_lk(version=version, slot=slot)  # Patch the binary
    log_success("Modified Little Kernel! Flashing back to device now.")
    flash_binary(dev, f"lk_{slot}.bin", gpt[f"lk_{slot}.bin"][0])
    log_success(
        "Done! To finalise the process, return to the previous menu and use fos_flags to gain root via ADB."
    )

    return


if __name__ == "__main__":
    main()
