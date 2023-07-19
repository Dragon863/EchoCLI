# EchoCLI
A tethered root solution for your echo dot 2nd generation.
## ⚠️ Warning!
- This is a TETHERED root solution
- It is _recommended_ to block amazon's OTA server (https://d1s31zyz7dcc2d.cloudfront.net) to prevent updates from corrupting or removing root on your device
- I am not responsible for any damage to your device

## Features
- Rooted ADB shell over USB or Wi-Fi
- Record audio from device
- Use your Echo as an indicator for Home Assistant without internet
- Restore your device to factory configuration

## Install
This project requires python 3.
I recommend using linux for running this program. Please ensure you have disabled ModemManager if you have it installed.
Install requirements using `pip`:
```sh
pip install -r requirements.txt
```

## Documentation
You can find how this tool works on [my website](https://dragon863.github.io/blog/).

Once you have rooted the device, a file called `preloader_no_hdr.bin` will be generated. To boot the device, you will need to install [mtkclient](https://github.com/bkerler/mtkclient), copy the file into its directory and run `python mtk plstage --preloader=preloader_no_hdr.bin`. Replace `python` with `python3` depending on the python version you have installed.

## Thanks

This project would not have been possible without:
- [j10hx40r](https://forum.xda-developers.com/m/j10hx40r.11878441/) - For helping me with initially rooting my device, showing me how to use fos_flags in combination and generally pointing me in the right direction when finding resources
- [xyzz's Amonet](https://github.com/xyzz/amonet) - This is the exploit I have adapted for this device, including the bootrom exploit
- [chaosmaster](https://github.com/chaosmaster) - Wrote lots of useful amonet code from which I used several snippets, including for fixing my GPT

## Contact me
- You can email me at dragon863.dev@gmail.com
- You can start a conversation on [XDA](https://forum.xda-developers.com/m/lemon86.12487447/)
