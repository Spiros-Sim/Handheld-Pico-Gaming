from machine import Pin,I2C,ADC
import time
import gc
import sh1106

WIDTH=128
HEIGHT=64

i2c=I2C(0,scl=Pin(5),sda=Pin(4),freq=400000)
oled=sh1106.SH1106_I2C(WIDTH,HEIGHT,i2c)
oled.sleep(False)

joystick_x=ADC(26)
joystick_y=ADC(27)
joystick_sw=Pin(16,Pin.IN,Pin.PULL_UP)
home_button=Pin(21,Pin.IN,Pin.PULL_UP)

JOYSTICK_CENTER=32500
JOYSTICK_DEADZONE=6000

import breakoutgame
import blackjack
import snake

GAMES=[
    ("BREAKOUT",breakoutgame.run),
    ("BLACKJACK",blackjack.run),
    ("SNAKE",snake.run)
]

selected_game=0

def clear():
    oled.fill(0)

def text_center(message,y):
    x=(WIDTH-len(message)*8)//2
    if x<0:
        x=0
    oled.text(message,x,y)

def button_pressed():
    if joystick_sw.value()==0:
        time.sleep_ms(30)
        if joystick_sw.value()==0:
            while joystick_sw.value()==0:
                time.sleep_ms(10)
            return True
    return False

def draw_home():
    clear()
    text_center("GAME CONSOLE",0)

    for i in range(len(GAMES)):
        y=18+i*14

        if i==selected_game:
            oled.text("> "+GAMES[i][0],10,y)
        else:
            oled.text("  "+GAMES[i][0],10,y)

    oled.show()

def handle_home():
    global selected_game

    value=joystick_y.read_u16()

    # Joystick up = previous game (higher on screen)
    if value>JOYSTICK_CENTER+JOYSTICK_DEADZONE:
        if selected_game>0:
            selected_game-=1
            draw_home()
            time.sleep_ms(200)

    # Joystick down = next game (lower on screen)
    elif value<JOYSTICK_CENTER-JOYSTICK_DEADZONE:
        if selected_game<len(GAMES)-1:
            selected_game+=1
            draw_home()
            time.sleep_ms(200)

    if button_pressed():
        launch_game()

def launch_game():
    while joystick_sw.value()==0:
        time.sleep_ms(10)

    clear()
    oled.show()
    gc.collect()

    game_function=GAMES[selected_game][1]

    game_function(
        oled,
        joystick_x,
        joystick_y,
        joystick_sw,
        home_button
    )

    gc.collect()

    while joystick_sw.value()==0:
        time.sleep_ms(10)

    draw_home()

def main():
    draw_home()

    while True:
        handle_home()
        time.sleep_ms(35)

main()