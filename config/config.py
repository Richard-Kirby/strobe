# Standard modules
import queue
import subprocess
import os

# Specialised modules
import gaugette.gpio
import pigpio

# Queue to send Display information.
DisplayQ = queue.Queue()

# Queue to send LED Control information.
LEDQ = queue.Queue()

"""
Start the pigpiod daemon up and running if it isn't already.

The pigpio daemon accesses the Raspberry Pi GPIO.  
"""
def InitPIGPIOD():

    global pi
    p = subprocess.Popen(['pgrep', '-f', 'pigpiod'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    if len(out.strip()) == 0:
        os.system("sudo pigpiod")

    # Set up the Pigpio Pi.  This is how pigpio is set up.
    pi = pigpio.pi()


