import time
import gc

WIDTH=128
HEIGHT=64

FPS_DELAY=35

PADDLE_WIDTH=24
PADDLE_HEIGHT=3
PADDLE_Y=60

BALL_SIZE=3

BRICK_WIDTH=10
BRICK_HEIGHT=5
BRICK_GAP=1

BRICK_START_X=3
BRICK_START_Y=10

LEVELS=[20,30,40,50,60]

TITLE=0
PLAYING=1
LEVEL_COMPLETE=2
GAME_OVER=3
YOU_WIN=4

game_state=TITLE

level=0
paddle_x=52

ball_x=64
ball_y=45

ball_dx=1
ball_dy=-1

ball_speed=1

bricks=[]

level_clear_time=0

JOYSTICK_CENTER=32500
JOYSTICK_DEADZONE=3000

BUTTON_DEBOUNCE=200

button_last=1
button_time=0

def initialize(o,jx,jy,js,hb):
    global oled
    global joystick_x
    global joystick_y
    global joystick_sw
    global home_button
    global button_last
    global button_time

    oled=o
    joystick_x=jx
    joystick_y=jy
    joystick_sw=js
    home_button=hb

    button_last=joystick_sw.value()
    button_time=time.ticks_ms()

def read_joystick():
    value=joystick_x.read_u16()

    if abs(value-JOYSTICK_CENTER)<JOYSTICK_DEADZONE:
        return 0

    if value<JOYSTICK_CENTER:
        return -1

    return 1

def joystick_pressed():
    global button_last
    global button_time

    current=joystick_sw.value()
    pressed=False

    if current==0 and button_last==1:
        now=time.ticks_ms()

        if time.ticks_diff(now,button_time)>BUTTON_DEBOUNCE:
            pressed=True
            button_time=now

    button_last=current
    return pressed

def check_home():
    if home_button.value()==0:
        time.sleep_ms(30)

        if home_button.value()==0:
            while home_button.value()==0:
                time.sleep_ms(10)

            return True

    return False

def clear():
    oled.fill(0)

def text_center(message,y):
    x=(WIDTH-len(message)*8)//2

    if x<0:
        x=0

    oled.text(message,x,y)

def generate_level():
    global bricks

    bricks=[]

    total=LEVELS[level]
    columns=12
    rows=(total+columns-1)//columns

    count=0

    for row in range(rows):
        for col in range(columns):

            if count>=total:
                break

            x=BRICK_START_X+col*(BRICK_WIDTH+BRICK_GAP)
            y=BRICK_START_Y+row*(BRICK_HEIGHT+BRICK_GAP)

            bricks.append([x,y,True])

            count+=1

def reset_ball():
    global ball_x
    global ball_y
    global ball_dx
    global ball_dy

    ball_x=64
    ball_y=45
    ball_dx=1
    ball_dy=-1

def start_game():
    global level
    global ball_speed
    global paddle_x
    global game_state

    level=0
    ball_speed=1
    paddle_x=52

    generate_level()
    reset_ball()

    game_state=PLAYING

def reset_game():
    global level
    global ball_speed
    global paddle_x
    global game_state

    level=0
    ball_speed=1
    paddle_x=52

    reset_ball()

    game_state=TITLE

def draw_paddle():
    oled.fill_rect(
        paddle_x,
        PADDLE_Y,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
        1
    )

def draw_ball():
    oled.fill_rect(
        int(ball_x),
        int(ball_y),
        BALL_SIZE,
        BALL_SIZE,
        1
    )

def draw_bricks():
    for brick in bricks:
        if brick[2]:
            oled.fill_rect(
                brick[0],
                brick[1],
                BRICK_WIDTH,
                BRICK_HEIGHT,
                1
            )

def draw_game():
    clear()

    oled.text(
        "LVL "+str(level+1),
        0,
        0
    )

    draw_bricks()
    draw_paddle()
    draw_ball()

    oled.show()

def draw_title():
    clear()

    text_center(
        "BREAK BRICKS",
        20
    )

    text_center(
        "Press Joystick",
        40
    )

    text_center(
        "A = HOME",
        52
    )

    oled.show()

def draw_game_over():
    clear()

    text_center(
        "GAME OVER",
        20
    )

    text_center(
        "Press Joystick",
        40
    )

    text_center(
        "GP21 = HOME",
        52
    )

    oled.show()

def draw_you_win():
    clear()

    text_center(
        "YOU WIN!",
        20
    )

    text_center(
        "Press Joystick",
        40
    )

    text_center(
        "GP21 = HOME",
        52
    )

    oled.show()

def draw_level_complete():
    clear()

    text_center(
        "LEVEL CLEAR",
        20
    )

    oled.show()

def update_paddle():
    global paddle_x

    direction=read_joystick()

    paddle_x+=direction*4

    if paddle_x<0:
        paddle_x=0

    if paddle_x+PADDLE_WIDTH>WIDTH:
        paddle_x=WIDTH-PADDLE_WIDTH

def check_paddle_collision():
    global ball_dy
    global ball_dx
    global ball_y

    if ball_dy>0:

        if (
            ball_y+BALL_SIZE>=PADDLE_Y and
            ball_y<=PADDLE_Y+PADDLE_HEIGHT and
            ball_x+BALL_SIZE>=paddle_x and
            ball_x<=paddle_x+PADDLE_WIDTH
        ):

            ball_y=PADDLE_Y-BALL_SIZE
            ball_dy=-1

            center=paddle_x+PADDLE_WIDTH//2

            if ball_x<center:
                ball_dx=-1
            else:
                ball_dx=1

def check_brick_collision():
    global ball_dy

    for brick in bricks:

        if brick[2]:

            bx=brick[0]
            by=brick[1]

            if (
                ball_x+BALL_SIZE>=bx and
                ball_x<=bx+BRICK_WIDTH and
                ball_y+BALL_SIZE>=by and
                ball_y<=by+BRICK_HEIGHT
            ):

                brick[2]=False
                ball_dy*=-1

                break

def update_ball():
    global ball_x
    global ball_y
    global ball_dx
    global ball_dy
    global game_state

    ball_x+=ball_dx*ball_speed
    ball_y+=ball_dy*ball_speed

    if ball_x<=0:
        ball_x=0
        ball_dx*=-1

    if ball_x+BALL_SIZE>=WIDTH:
        ball_x=WIDTH-BALL_SIZE
        ball_dx*=-1

    if ball_y<=8:
        ball_y=8
        ball_dy*=-1

    if ball_y>HEIGHT:
        game_state=GAME_OVER
        return

    check_paddle_collision()
    check_brick_collision()

def level_finished():
    for brick in bricks:
        if brick[2]:
            return False

    return True

def next_level():
    global level
    global ball_speed
    global game_state

    if level>=4:
        game_state=YOU_WIN
        return

    level+=1
    ball_speed+=1

    generate_level()
    reset_ball()

    game_state=PLAYING

def handle_title():
    if joystick_pressed():
        start_game()

def handle_playing():
    global game_state
    global level_clear_time

    update_paddle()
    update_ball()

    if level_finished():
        game_state=LEVEL_COMPLETE
        level_clear_time=time.ticks_ms()

def handle_level_complete():
    if time.ticks_diff(
        time.ticks_ms(),
        level_clear_time
    )>1500:

        next_level()

def handle_game_over():
    if joystick_pressed():
        reset_game()

def handle_win():
    if joystick_pressed():
        reset_game()

def run(o,jx,jy,js,hb):
    global game_state

    initialize(
        o,
        jx,
        jy,
        js,
        hb
    )

    game_state=TITLE

    last_state=-1

    while True:

        if check_home():
            clear()
            oled.show()
            gc.collect()
            return

        if game_state!=last_state:

            if game_state==TITLE:
                draw_title()

            elif game_state==GAME_OVER:
                draw_game_over()

            elif game_state==YOU_WIN:
                draw_you_win()

            elif game_state==LEVEL_COMPLETE:
                draw_level_complete()

            last_state=game_state

        if game_state==TITLE:
            handle_title()

        elif game_state==PLAYING:
            handle_playing()
            draw_game()

        elif game_state==LEVEL_COMPLETE:
            handle_level_complete()

        elif game_state==GAME_OVER:
            handle_game_over()

        elif game_state==YOU_WIN:
            handle_win()

        time.sleep_ms(FPS_DELAY)