#!/usr/bin/python3

# Standard Packages
import time

# Custom packages

# Project Modules
import display.display as display
import config.config as config
import led.led as led
import config.config as config
import decoder.decoder as rotary_encoder


# Rotary pin setup
ROTARY_A_PIN = 4 # A Pin of the rotary encoder
ROTARY_B_PIN = 2 # B Pin of the rotary encoder

# GPIO used for monitoring the switch.
ROTARY_SW_PIN = 3 # Switch Pin for the rotary encoder

on_off_state =0 # Start with strobe off.

# start at 10Hz.
Hz = init_Hz = 10
pos = 0


def update_threads():
    global on_off_state
    global Hz

    # String for updating the threads - display and LED strip.
    update_str = "<STROBE><ON_OFF_STATE>{:d}</ON_OFF_STATE><FREQ>{:d}</FREQ></STROBE>".format(on_off_state, Hz)

    # Put new config into the display
    config.DisplayQ.put_nowait(update_str)

    # Put new config to the LED Thread
    config.LEDQ.put_nowait(update_str)


# Callback function to deal with rotary encoder rotational changes.
def rotary_encoder_rotation_callback(way):
    global pos
    global Hz

    # Update position with the value received from callback
    Hz += way

    # Restrict to 0 - which means fully on.
    if Hz < 0:
        Hz = 0

    # Update the threads to reflect new setting.
    update_threads()


# Callback function to deal with a change to the switch
def rotary_switch_callback():
    global on_off_state

    on_off_state = not on_off_state

    # Update the threads to reflect new setting.
    update_threads()

if __name__ == "__main__":
    try:
        # Start PIGPIOD
        config.InitPIGPIOD()

        # Start up the various threads.

        # Display Thread.
        DisplayThread = display.DisplayThread(1, "Display Thread", 1)
        DisplayThread.start()

        # Start up LED String
        led_thread = led.LEDThread(1, "LED Thread", 1)
        led_thread.start()

        # Initialise the display
        update_threads()

        # Decoder object created with the information for rotary changes as well as the included switch.
        decoder = rotary_encoder.decoder(config.pi, ROTARY_A_PIN, ROTARY_B_PIN, ROTARY_SW_PIN,
                                         rotary_encoder_rotation_callback, rotary_switch_callback )

    # Handle Ctrl-C case.
    except KeyboardInterrupt:
            print("Fine - quit see if I care - jerk")

            on_off_state = 0

            # Update the threads to reflect new setting.
            update_threads() # Turning off strobe

            time.sleep(1)
            DisplayThread.join()
            led_thread.join()

            decoder.cancel()
            config.pi.stop()
            exit()