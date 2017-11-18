#!/usr/bin/python3

# Standard Packages
import time

# Custom packages

# Libraries for the RotaryEncoder class and the Switch class.
# The common pin for the encoder should be wired to ground.
# The sw_pin should be shorted to ground by the switch.
#import gaugette.rotary_encoder
#import gaugette.switch

# Project Modules
import display.display as display
import config.config as config
import led.led as led
import config.config as config
import decoder.decoder as rotary_encoder


# Rotary pin setup
ROTARY_A_PIN = 4 # A Pin of the rotary encoder
ROTARY_B_PIN = 2 # B Pin of the rotary encoder

ROTARY_SW_PIN = 3 # Switch Pin for the rotary encoder

# Set up the encoder device.
#switch = gaugette.switch.Switch(config.gpio, ROTARY_SW_PIN)

last_state = None
current_pos =0
last_pos =0
on_off_state =0 # Start with strobe off.

# start at 10Hz.
Hz=init_Hz = 10

pos = 0

def update_threads():
    global on_off_state
    global Hz
    # Put new config into the display

    update_str = "<STROBE><ON_OFF_STATE>{:d}</ON_OFF_STATE><FREQ>{:d}</FREQ></STROBE>".format(on_off_state, Hz)
    config.DisplayQ.put_nowait(update_str)

    # Put new config to the LED Thread
    config.LEDQ.put_nowait(update_str)


def rotary_encoder_rotation_callback(way):
    global pos
    global Hz

    pos += way

    Hz = init_Hz + int(pos)

    if Hz<1:
        Hz =1

    update_threads()

    #print("Hz={}".format(Hz))

# Deal with a change to the switch
def rotary_switch_callback():
    global on_off_state

    on_off_state = not on_off_state
    update_threads()

if __name__ == "__main__":
    try:
        # Start up the various threads.

        # Display Thread.
        DisplayThread = display.DisplayThread(1, "Display Thread", 1)
        DisplayThread.start()

        # Start up LED String
        led_thread = led.LEDThread(1, "LED Thread", 1)
        led_thread.start()

        # Initialise the display
        update_threads()

        decoder = rotary_encoder.decoder(config.pi, ROTARY_A_PIN, ROTARY_B_PIN, ROTARY_SW_PIN,
                                         rotary_encoder_rotation_callback, rotary_switch_callback )

        while True:

            0

            #sw_state = switch.get_state()

            # Process change in state.
            #if sw_state != last_state:
            #   #print("switch %d" % sw_state)
            #  last_state = sw_state

            #    change = True

            #   # Toggle on/off when switch is pressed.
            #   if sw_state == 1:
            #        on_off_state = not on_off_state # toggle on/off state.


    except KeyboardInterrupt:
            print("Fine - quit see if I care - jerk")
            decoder.cancel()
            config.pi.stop()

            exit()