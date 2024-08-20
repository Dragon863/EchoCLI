# Restore device using mtkclient
Make sure you have the tools wget, mtkclient and unzip installed

1. Open a new terminal and run `mkdir OTA && cd OTA`
2. Go to https://github.com/ssut/payload-dumper-go and download the appropriate release for your CPU architecture, extract it in the OTA directory using tar -xzf [filename]
3. Run `wget https://d1s31zyz7dcc2d.cloudfront.prod.ota-cloudfront.net/cd5c2a08fa0de682af56c9f7f14512b2/update-kindle-biscuit_puffin-NS6559_user_4660_0009094444164.bin && unzip update-kindle-biscuit_puffin-NS6559_user_4660_0009094444164.bin` then `./payload-dumper-go payload.bin`. This will download FireOS 6.5.5.9 from Amazon and extract the contents from the payload.bin file.
4. A new directory will be created called `extracted_[timestamp]` where timestamp is the current time . Run `cd [directoryname]`
5. Rename the files `lk.img`, `boot.img` and `system.img` to `lk_a.img`, `boot_a.img` and `system_a.img` respectively,  and then make copies of these, replacing the `_a` for `_b`, for example `lk_b.img`. After this, rename tee.img to tee1.img and make a copy of it called tee2.img . It is probably easiest to complete this step in a file manager. The directory will look like this:
![files](https://i.imgur.com/c7KhCQe.png)
6. Plug in your echo. It will boot into "bootrom" mode after the blue lights have stopped, you will know this because the lights will turn off and it will show as `0e8d:0003 MediaTek Inc. MT6227 phone` in `lsusb`.
7. Clone the [mtkclient](https://github.com/bkerler/mtkclient) repository to your computer if you have not done so already, then run `sudo mtk wl . --preloader [path to mtkclient]/Loader/Preloader/preloader_biscuit.bin`

This should flash your device to stock firmware. You will have to re-run EchoCLI afterwards, but once you have run step 7 you should first unplug your device to check that it boots correctly.
