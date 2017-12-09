import config.config as config


# Decoder class for use with a rotary encoder.
class decoder:

    """Class to decode mechanical rotary encoder pulses."""

    def __init__(self, pi, rot_gpioA, rot_gpioB, switch_gpio, rotation_callback, switch_callback):

        """
        Instantiate the class with the pi and gpios connected to
        rotary encoder contacts A and B.  The common contact
        should be connected to ground.  The callback is
        called when the rotary encoder is turned.  It takes
        one parameter which is +1 for clockwise and -1 for
        counterclockwise.

        EXAMPLE

        import time
        import pigpio

        import rotary_encoder

        pos = 0

        def callback(way):

         global pos

         pos += way

         print("pos={}".format(pos))

        pi = config.pigpio.pi()

        decoder = rotary_encoder.decoder(pi, 7, 8, callback)

        time.sleep(300)

        decoder.cancel()

        pi.stop()

        """

        self.pi = pi
        self.rot_gpioA = rot_gpioA
        self.rot_gpioB = rot_gpioB


        self.rot_callback = rotation_callback
        self.sw_callback = switch_callback

        self.levA = 0
        self.levB = 0

        self.lastGpio = None

        # Setting up rotary encoder, including callback.
        self.pi.set_mode(rot_gpioA, config.pigpio.INPUT)
        self.pi.set_mode(rot_gpioB, config.pigpio.INPUT)

        self.pi.set_pull_up_down(rot_gpioA, config.pigpio.PUD_UP)
        self.pi.set_pull_up_down(rot_gpioB, config.pigpio.PUD_UP)

        self.cbA = self.pi.callback(rot_gpioA, config.pigpio.EITHER_EDGE, self._pulse)
        self.cbB = self.pi.callback(rot_gpioB, config.pigpio.EITHER_EDGE, self._pulse)

        # Setting up switch of rotary encoder.
        self.pi.set_mode(switch_gpio, config.pigpio.INPUT)
        self.pi.set_mode(switch_gpio, config.pigpio.INPUT)

        self.pi.set_pull_up_down(switch_gpio, config.pigpio.PUD_UP)
        self.pi.set_pull_up_down(switch_gpio, config.pigpio.PUD_UP)

        self.switch_cb = self.pi.callback(switch_gpio, config.pigpio.RISING_EDGE, self._switch_toggle)

    # Handles the switch part of the rotary encoder.
    def _switch_toggle(self, gpio, level, tick):
        self.sw_callback()



    def _pulse(self, gpio, level, tick):

        """
        Decode the rotary encoder pulse.

                   +---------+         +---------+      0
                   |         |         |         |
         A         |         |         |         |
                   |         |         |         |
         +---------+         +---------+         +----- 1

             +---------+         +---------+            0
             |         |         |         |
         B   |         |         |         |
             |         |         |         |
         ----+         +---------+         +---------+  1
        """

        if gpio == self.rot_gpioA:
            self.levA = level
        else:
            self.levB = level;

        if gpio != self.lastGpio: # debounce
            self.lastGpio = gpio

        if   gpio == self.rot_gpioA and level == 1:
            if self.levB == 1:
                self.rot_callback(1)

        elif gpio == self.rot_gpioB and level == 1:
            if self.levA == 1:
                self.rot_callback(-1)

    def cancel(self):

        """
        Cancel the rotary encoder decoder.
        """

        self.cbA.cancel()
        self.cbB.cancel()

if __name__ == "__main__":

    import time
    import pigpio

    import rotary_encoder

    pos = 0

    def callback(way):

        global pos

        pos += way

        print("pos={}".format(pos))

    pi = pigpio.pi()

    decoder = rotary_encoder.decoder(pi, 2, 4, callback)

    time.sleep(300)

    decoder.cancel()

    pi.stop()