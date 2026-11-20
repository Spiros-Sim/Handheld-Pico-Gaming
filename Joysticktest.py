from machine import ADC
import time

joystick_x = ADC(26)

while True:

    value = joystick_x.read_u16()

    print(value)

    time.sleep_ms(100)