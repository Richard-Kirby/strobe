# Standard modules
import queue

# Specialised modules
import gaugette.gpio
import pigpio

# Queue to send Display information.
DisplayQ = queue.Queue()

# Queue to send LED Control information.
LEDQ = queue.Queue()

# Set up GPIO to be used by various modules.
#gpio = gaugette.gpio.GPIO()

pi= pigpio.pi()

