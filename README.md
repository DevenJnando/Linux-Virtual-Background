# Credit to Benjamin Elder:
This project was inspired and based on the work of one Benjamin Elder who made a similar implementation using bodypix
and docker. I thought the end result of his project was fantastic, but I found the installation/running steps tedious
and irritating to set up. 

This work is my attempt to remedy these issues. I also found bodypix to be slow and somewhat
flaky. The bodypix implementation has been replaced with mediapipe.

Here is a link to Benjamin's original blog post: https://elder.dev/posts/open-source-virtual-background/ 

check him out,
he's a talented dude!
# Dependencies:
## Python:
Please look over `requirements.txt` and use this file to install the necessary dependencies.

## Debian:
There is also one linux dependency necessary for this script to work: v4l2loopback. This can be installed with 
the following command:

`sudo apt-get install v4l2loopback-utils`

# How to use:
##Modprobing a dummy webcam device:
You can create a new dummy webcam device with this command:

`sudo modprobe v4l2loopback devices=1 exclusive_caps=1 video_nr=2 card_label="virtual-background-output"`

The `exclusive_caps=1` argument is necessary for some programs such as Google Chrome and Zoom. Once you're finished, 
you can remove the dummy camera using this command:

`sudo rmmod -r v4l2loopback`

## Running the script:
After the v4l2loopback device has been modprobed, use the command `python virtual_backgrounds.py` 
to run using the default config.

You can use the `-o` or `--output` argument to change the file path of your dummy webcam. You can also use `-b` or
`--background_image` to change the file path of your background image.

Some example backgrounds are included in the `backgrounds` directory. Feel free to add more to your local copy.
The default background is currently set to Burzum's Filosofem album artwork. 

## Effects:
You can add some effects as well if you like. To add effects, simply set the relevant effect argument to true, e.g. `--sepia true`

## A note on Burzum:

If you haven't listened to any Burzum before, then
stop fiddling with virtual backgrounds and go listen to Filosofem right now. Give it your full attention. If you don't like it, that's
fine, but do understand this, dear reader: it's not Varg and his music which is at fault, it is entirely *you* in
the wrong. Peace and love!
