# Standard libraries
import threading
import time
import xml.etree.ElementTree as XML_ET

# Project libraries
import config.config as config

# Basic setup of the pins
RLED_PIN=14
GLED_PIN=15
BLED_PIN=18

# Set up the LEDs
#led = gaugette.rgbled.RgbLed(config.gpio, RLED_PIN, BLED_PIN, GLED_PIN)

# Thread to handle the LED pulsing for the strobe.
class LEDThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)

        red_state = 1
        green_state = 1
        blue_state = 1
        freq_str = 10

        # Go through a range of frequencies just to check things out.
        while True:

            # Process anything in the LED Queue
            if not config.LEDQ.empty():

                # Skip to the last item in the queue - could be adding faster than can process.
                while not config.LEDQ.empty():
                    ledq_str = config.LEDQ.get_nowait()

                #print(ledq_str)

                # Process the XML information.
                led_et = XML_ET.fromstring(ledq_str)

                # Parse the display information
                for element in led_et:
                    if (element.tag =="RED"):
                        red_state= int(element.text)
                    if (element.tag =="GREEN"):
                        green_state= int(element.text)
                    if (element.tag =="BLUE"):
                        blue_state= int(element.text)
                    if (element.tag == "FREQ"):
                        freq_str = element.text
                    if int(freq_str) < 1:
                        freq_str = 1

                #led.set(red_state, green_state, blue__state)
                # Set up the stobe frequencies to the specified rate.
                config.pi.set_PWM_frequency(RLED_PIN, int(freq_str))
                config.pi.set_PWM_frequency(GLED_PIN, int(freq_str))
                config.pi.set_PWM_frequency(BLED_PIN, int(freq_str))
                config.pi.set_PWM_dutycycle(RLED_PIN, red_state*128)
                config.pi.set_PWM_dutycycle(GLED_PIN, green_state*128)
                config.pi.set_PWM_dutycycle(BLED_PIN, blue_state*128)

        print("Exiting " + self.name)

        # Shutdown the pigpio
        config.pi.stop()
        exit()
