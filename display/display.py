# Copyright (c) 2017 Richard Kirby richard.james.kirby@gmail.com
# Modified code from Adafruit Tony DiCola - see below
#
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import threading
import time
import xml.etree.ElementTree as XML_ET

import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

# Project Modules
import config.config as config

# Setting up the display constants.
WIDTH = 128
HEIGHT = 160
SPEED_HZ = 4000000
FONT_SIZE = 36

# Raspberry Pi configuration.  Some basic setups and pin definitions.
DC = 22
RST = 27
SPI_PORT = 0
SPI_DEVICE = 0

# Create TFT LCD display class.
disp = TFT.ST7735(
    DC,
    rst=RST,
    spi=SPI.SpiDev(
        SPI_PORT,
        SPI_DEVICE,
        max_speed_hz=SPEED_HZ),
    width=WIDTH,
    height=HEIGHT)

# Initialize display.
disp.begin()

# Clear the display to a red background.
# Can pass any tuple of red, green, blue values (from 0 to 255 each).
# disp.clear((0, 0, 0))

# Clear to a black screen.
disp.clear()

# Get a PIL Draw object to start drawing on the display buffer.
draw = disp.draw()

# Load a font - Hack is a mono-space font.
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/home/pi/strobe/Hack-Bold.ttf', FONT_SIZE)


# Define a function to create rotated text.  Unfortunately PIL doesn't have good
# native support for rotated fonts, but this function can be used to make a
# text image and rotate it so it's easy to paste in the buffer.
def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)

    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))

    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0, 0), text, font=font, fill=fill)

    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)

    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)


# Thread to handle outputting to the OLED screen and sending to the server.
# - to avoid spending too much time blocked on this.
class DisplayThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)

        on_off_state = 0

        last_on_off_state= 2 # Out of range to make sure display at the start.
        freq =0.0

        # Dealing with Queue
        while (1):

            # Process anything in the display Queue
            if not config.DisplayQ.empty():

                while not config.DisplayQ.empty(): # Get to the last item - may be a backlog
                    display_str = config.DisplayQ.get_nowait()

                # Process the XML information.
                display_et = XML_ET.fromstring(display_str)

                # Parse the display information
                for element in display_et:
                    if (element.tag =="ON_OFF_STATE"):
                        on_off_state= int(element.text)
                    if (element.tag == "FREQ"):
                        freq_str = element.text + "Hz"

                # Draw a rectangle as a way of refreshing the display.
                draw.rectangle((40, 3, 80, 155), outline=(0, 0, 255), fill=(0, 0, 0))

                # Display the Frequency.
                draw_rotated_text(disp.buffer, freq_str, (int((WIDTH - FONT_SIZE) / 2), 30), 270, font, fill=(255, 255, 255))

                if last_on_off_state != on_off_state:
                    draw.rectangle((0, 0, 35, 155), outline=(0, 0, 0), fill=(0, 0, 0))

                    # Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
                    if on_off_state == 0:
                        draw_rotated_text(disp.buffer, "Off", (0, 0), 270, font, fill=(0, 0, 255))  # Blue, Green, Red

                    elif on_off_state == 1:
                        draw_rotated_text(disp.buffer, "On", (0, 110), 270, font, fill=(0, 255, 0))  # Blue, Green, Red
                    else:
                        print("Couldn't process on/off state")

                # Write buffer to display hardware, must be called to make things visible on the
                # display!
                disp.display()

        print("Exiting " + self.name)
        exit()
