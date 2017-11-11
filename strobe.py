#!/usr/bin/python3

# Standard Packages
import time

# Custom packages

# Libraries for the RotaryEncoder class and the Switch class.
# The common pin for the encoder should be wired to ground.
# The sw_pin should be shorted to ground by the switch.
import gaugette.rotary_encoder
import gaugette.switch

# Project Modules
import display.display as display
import config.config as config
import led.led as led
import config.config as config


# Rotay pin setup
ROTARY_A_PIN = 7 # A Pin of the rotary encoder
ROTARY_B_PIN = 8 # B Pin of the rotary encoder
ROTARY_SW_PIN = 9 # Switch Pin for the rotary encoder

# Set up the encoder device.
encoder = gaugette.rotary_encoder.RotaryEncoder.Worker(config.gpio, ROTARY_A_PIN, ROTARY_B_PIN)
encoder.start()
switch = gaugette.switch.Switch(config.gpio, ROTARY_SW_PIN)

last_state = None
current_pos =0
last_pos =0
on_off_state =0 # Start with strobe off.

# start at 10Hz.
Hz=init_Hz = 10

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
        config.DisplayQ.put_nowait("<DISPLAY><ON_OFF_STATE>{:d}</ON_OFF_STATE><FREQ>{:03.1f}Hz</FREQ></DISPLAY>".format(on_off_state, Hz))

        # Default setup for noting a change in settings.
        change = False

        while True:

            # Get information from the encoder.
            delta = encoder.get_steps()

            if delta != 0:
                current_pos += delta
                #print("rotate %d" % delta)
                #print("Current position = {}".format(current_pos))
                # Calculate the delay to be used for the strobe, use negative numbers so turning
                # clockwise results in increase in frequency.
                #delay = int(initial_delay - current_pos)
                Hz = init_Hz + int(current_pos/4)
                change = True

            else:
                time.sleep(0.005)

            # Check the state of the switch - looking for toggle.
            sw_state = switch.get_state()

            # Process change in state.
            if sw_state != last_state:
                #print("switch %d" % sw_state)
                last_state = sw_state

                change = True

                # Toggle on/off when switch is pressed.
                if sw_state == 1:
                    on_off_state = not on_off_state # toggle on/off state.


            if change: # either on/off or frequency change has occurred - tell the threads

                # Put new config into the display
                config.DisplayQ.put_nowait(
                    "<DISPLAY><ON_OFF_STATE>{:d}</ON_OFF_STATE><FREQ>{:d}Hz</FREQ></DISPLAY>".format(on_off_state, int(Hz)))

                # Put new config to the LED Thread
                config.LEDQ.put_nowait(
                    "<LED><RED>{:d}</RED><BLUE>{:d}</BLUE><GREEN>{:d}</GREEN><FREQ>{:d}</FREQ></LED>"
                         .format(on_off_state,on_off_state,on_off_state, int(Hz)))

                # After processing set change to False and wait for next change.
                change = False

    except KeyboardInterrupt:
            print("Fine - quit see if I care - jerk")

            exit()