# Standard libraries
import threading
import time
import xml.etree.ElementTree as XML_ET

# Project libraries
import config.config as config

# Basic setup of the pins
STROBE_PIN=13

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

            try:
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
                        if (element.tag == "ON_OFF_STATE"):
                            on_off_state = int(element.text)
                        if (element.tag == "FREQ"):
                            freq_str = element.text

                    # Set up the strobe frequencies to the specified rate.
                    if int(freq_str) == 0:
                        config.pi.hardware_PWM(STROBE_PIN, 10, on_off_state * 1000000)
                    else:
                        config.pi.hardware_PWM(STROBE_PIN, int(freq_str), on_off_state*100000)
            except KeyboardInterrupt:
                # Turn off strobe in case it is currently on
                config.pi.hardware_PWM(STROBE_PIN, 10, 0)
                config.pi.stop()
                print("Exiting " + self.name)

        # Shutdown the pigpio
        config.pi.stop()
        exit()
