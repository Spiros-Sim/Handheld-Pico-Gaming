# Handheld-Pico-Gaming
I made a handheld pico gaming device by combining a Raspberry Pi Pico with a Ky-023 joystick, pushbutton, 1.3 inch OLED screen, and a repurposed battery and charging circuit. I have included the codes, enclosure, and the pin layout.


**PIN Layout******
Display
  Gnd-.Gnd
  VCC-3.3v
  Sck->GP05       
  SDA-> GP04       

Button
  Gnd->Gnd
  VCC -> 3.3v
  S -> GP21

Joystick
  Gnd -> Gnd
  VCC -> 3.3v
  VRX -> AD27
  VRY -> AD26
  SW -> GP16
