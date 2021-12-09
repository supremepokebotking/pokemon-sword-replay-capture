# pokemon-sword-replay-capture
This is an old version (March 2020) pokemon-sword-replay-capture-mar-2020-version of my Pokemon Replay Capture software. I built this to try my reinforcement learning environments on the real game.

## Haven't Ran this code since 2020.
## I did updated the yolo_poke_runner.py file to use the newest yolov3 model.
# You can edit yolo_poke_runner.py if you want to use the 2020 yolov3 model.

## Features that may exist partially or in full
The ability to add dynamic voices to Pokemon matches. may need more work
The ability to play wild and network fights

## Assume unfixed bugs. I saved this state based on a particular date and not state of the project.

Need Help?
Discord
Current link: https://discord.gg/7cu6mrzH

# To get started. Assuming you have an USB-HDMI Capture card such as Elgato Cam Link or another brand and the right arduino, you should be fine.

## Hardware Requirements
A flashed Arduino with this dex: https://github.com/shinyquagsire23/Switch-Fightstick
USB to serial Adapter or breakout.
USB Hdmi Capture Card.
For reference:  https://betterprogramming.pub/creating-a-fake-nintendo-switch-controller-to-level-up-my-character-in-world-of-final-fantasy-b50adc269a1e

Video Of Project Working:  https://vimeo.com/654820810

You can extract sword_capture_trained_model_40.zip into the models/ directory:
https://www.dropbox.com/s/cpwmg3l2306bpec/sword_capture_trained_model_40.zip?dl=0


## Commands To Get you started.
To get the USB serials connected to you device run:  python3 available_serial.py
You should see something like: ['/dev/tty.Bluetooth-Incoming-Port', '/dev/tty.usbserial-AQ00LCW6']
Windows and linux will look different.
Update switch_button_prss.py with you value. In my case I use '/dev/tty.usbserial-AQ00LCW6' on line 18
Next Step make sure your web cam is working.
open webcam_test.py and change line 12 until you figure out which device is your capture card.
Press ESC or Q to close.
Open yolo_state_tracker_opencv.py and update line 5423 to open the same device. This is inside of the process_live_video_feed2345 function.

At this point Start A wild Match in Pokemon Sword or Shield then run:
python3 yolo_poke_runner.py

If there are crashes from no imports, just install with pip.
Some examples are: stable_baselines, and baselines
If you cant install baselines, comment out line #22 inside of yolo_state_tracker_opencv.py which imports AiNetwork: "from ainetwork import AiNetwork"
This isnt an issue because by default the bot is random. 

  pokemon-sword-replay-capture is free for most use cases and the source is available. The source code is published
  under the [Server Side Public License (SSPL) v1](LICENSE.txt).
