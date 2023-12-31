import struct
import datetime
import hashlib
import shutil
import os
import sys

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
    sys.exit(1)


def log_success(msg: str):
    current_time = datetime.datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"[{formatted_time}] \033[92mSUCCESS:\x1b[0m", msg)


def is_patched(slot: str):
    data = b''
    patch = bytes.fromhex('0120704700214ff4')
    with open(f"lk_{slot}.bin", "rb") as f:
        data = f.read()
    return data.find(patch) > -1

def modify_lk(slot: str):
    data = b''
    pattern = bytes.fromhex('10b5c0b000214ff4')
    patch = bytes.fromhex('0120704700214ff4')
    with open(f"lk_{slot}.bin", "rb") as f:
        data = f.read()
    if data.find(pattern) == -1:
        log_fail('Pattern not found. Lk can not be patched')
    data = data.replace(pattern, patch)
    with open(f"lk_{slot}.bin", "wb") as f:
        f.write(data)


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


def check_boot_slot():
    index = -1
    data = b''
    slot = "b"
    with open("misc.bin", "rb") as file:
        data = file.read()
        index = data.find(b'ABB')
    if data[index+4] > data[index+5]:
        slot = "a"
    return slot


def check_preloader():
    with open("preloader.bin", "rb") as f:
        buffer = f.read(32)
    return buffer[:9] == b'EMMC_BOOT' and struct.unpack("<I", buffer[0x10:0x14])[0] != 0


def extract_preloader():
    preloader = b''
    with open("preloader.bin", "rb") as f:
        preloader = f.read()
        start = preloader.find(b'MMM')
        length = struct.unpack("<I", preloader[start+0x20:start+0x24])[0]
        preloader = preloader[start:start+length]

    pattern_5xxx = bytes.fromhex('73b506464ff4c060')
    pattern_6xxx = bytes.fromhex('2de9f046cfb00c46')
    if preloader.find(pattern_6xxx):
        log_info("6.x preloader detected, applying unlock patch")
        patch = bytes.fromhex('00207047cfb00c46')
        preloader = preloader.replace(pattern_6xxx, patch)
    elif preloader.find(pattern_5xxx):
        log_info("5.x preloader detected, applying unlock patch")
        patch = bytes.fromhex('012070474ff4c060')
        preloader = preloader.replace(pattern_5xxx, patch)
    else:
        log_fail("Unknown preloader detected, we can not patch the same")

    with open("../../preloader_no_hdr.bin", "wb") as f:
        f.write(preloader)


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

    switch_user(dev)
    log_info("Fetching misc partition...")
    dump_binary(dev, "misc.bin", gpt["misc"][0] + 1, 1)
    slot=check_boot_slot()
    log_info(f"Detected that device is using slot {slot.upper()}.")

    if choice.lower() == "restore":
        switch_boot0(dev)
        log_info("Restoring preloader...")
        flash_binary(dev, "backup/preloader.bin", 0)

        log_info("Downgrading rpmb header")
        dev.rpmb_write(b"\x00" * 0x100)
        rpmb = dev.rpmb_read()
        if rpmb != b"\x00" * 0x100:
            dev.reboot()
            log_fail("downgrade failure, giving up")
        log_info("rpmb downgrade ok")

        switch_user(dev)
        if f"lk_{slot}.bin" in os.listdir("backup/"):
            log_info(f"Restoring lk_{slot} partition...")
            flash_binary(dev, f"backup/lk_{slot}.bin", gpt[f"lk_{slot}"][0])
        log_success(
            "Restored device! If you experience any problems, please contact me."
        )
        return

    switch_boot0(dev)
    log_info(
        """
        This next step WILL brick your preloader, rendering your device unbootable without a computer, as this is a TETHERED exploit. This is a reversible change. Press enter if you understand the consequences and accept that I am not responsible for any damage to you device...
        """
    )
    input()
    log_info("Backing up preloader...")
    dump_binary(dev, "preloader.bin", 0, 1024)
    if check_preloader():
        shutil.copyfile("preloader.bin", "backup/preloader.bin")
        log_info("Clearing preloader header")
        # Thanks to chaosmaster for this useful snippet
        flash_data(dev, b"EMMC_BOOT" + b"\x00" * ((0x200 * 8) - 9), 0)
    else:
        log_info("Looks like this preloader was already cleared. Skipping clearing and backup steps...")

    extract_preloader()
    log_info("Downgrading rpmb header")
    dev.rpmb_write(b"\x00" * 0x100)
    rpmb = dev.rpmb_read()
    if rpmb != b"\x00" * 0x100:
        dev.reboot()
        log_fail("downgrade failure, giving up")
    log_info("rpmb downgrade ok")

    switch_user(dev)
    nonzero = []
    log_info(f"Backing up lk_{slot}...")
    dump_binary(dev, f"lk_{slot}.bin", gpt[f"lk_{slot}"][0], gpt[f"lk_{slot}"][1])
    if is_patched(slot):
        log_info(f"LK is already patched. Exiting...")
        return
    shutil.copyfile(f"lk_{slot}.bin", f"backup/lk_{slot}.bin")
    modify_lk(slot=slot)  # Patch the binary
    log_success("Modified Little Kernel! Flashing back to device now.")
    flash_binary(dev, f"lk_{slot}.bin", gpt[f"lk_{slot}"][0])
    log_success(
        "Done! To finalise the process, return to the previous menu and use fos_flags to gain root via ADB."
    )

    return


if __name__ == "__main__":
    main()
