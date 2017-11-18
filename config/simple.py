import time
import pigpio

pi= pigpio.pi()
pin=13

print("Hardware revision ",pi.get_hardware_revision())
print("PIGPIO Version ",pi.get_pigpio_version())

while True:
    pi.write(pin, 1)
    print(pin, "-on")
    time.sleep(2)
    pi.write(pin, 0)
    print(pin, "-off")
    time.sleep(2)

