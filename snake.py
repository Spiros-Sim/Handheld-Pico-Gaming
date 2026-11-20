import time
import gc

WIDTH = 128
HEIGHT = 64

FPS_DELAY = 120

# Joystick calibration
JOYSTICK_CENTER = 32000
JOYSTICK_DEADZONE = 6000

# Game area
TOP = 9
BOTTOM = 63

# Snake settings
SNAKE_SIZE = 4
MAX_SNAKE = 150

# States
TITLE = 0
PLAYING = 1
GAME_OVER = 2

game_state = TITLE

# Hardware
oled = None
joystick_x = None
joystick_y = None
joystick_sw = None
home_button = None

# Snake
snake = []
food_x = 80
food_y = 30

direction = (1, 0)
next_direction = (1, 0)

score = 0

button_last = 1
button_time = 0

BUTTON_DEBOUNCE = 200


# -------------------------------------------------
# INITIALIZATION
# -------------------------------------------------

def initialize(o, jx, jy, js, hb):
    global oled
    global joystick_x
    global joystick_y
    global joystick_sw
    global home_button
    global button_last
    global button_time

    oled = o
    joystick_x = jx
    joystick_y = jy
    joystick_sw = js
    home_button = hb

    button_last = joystick_sw.value()
    button_time = time.ticks_ms()


# -------------------------------------------------
# JOYSTICK
# -------------------------------------------------

def read_joystick():
    """
    Returns:
        -1, 0, or 1 for X
        -1, 0, or 1 for Y
    """

    x = joystick_x.read_u16()
    y = joystick_y.read_u16()

    dx = 0
    dy = 0

    if x < JOYSTICK_CENTER - JOYSTICK_DEADZONE:
        dx = -1

    elif x > JOYSTICK_CENTER + JOYSTICK_DEADZONE:
        dx = 1

    if y < JOYSTICK_CENTER - JOYSTICK_DEADZONE:
        dy = 1

    elif y > JOYSTICK_CENTER + JOYSTICK_DEADZONE:
        dy = -1

    return dx, dy


def joystick_pressed():
    global button_last
    global button_time

    current = joystick_sw.value()
    pressed = False

    if current == 0 and button_last == 1:

        now = time.ticks_ms()

        if time.ticks_diff(now, button_time) > BUTTON_DEBOUNCE:
            pressed = True
            button_time = now

    button_last = current

    return pressed


# -------------------------------------------------
# HOME BUTTON
# -------------------------------------------------

def check_home():

    if home_button.value() == 0:

        time.sleep_ms(30)

        if home_button.value() == 0:

            while home_button.value() == 0:
                time.sleep_ms(10)

            return True

    return False


# -------------------------------------------------
# DISPLAY
# -------------------------------------------------

def clear():
    oled.fill(0)


def text_center(message, y):

    x = (WIDTH - len(message) * 8) // 2

    if x < 0:
        x = 0

    oled.text(message, x, y)


# -------------------------------------------------
# FOOD
# -------------------------------------------------

def place_food():

    global food_x
    global food_y

    # Generate a pseudo-random position using the
    # current timer value.

    seed = time.ticks_ms()

    food_x = 4 + ((seed * 17) % (WIDTH - 8))
    food_y = TOP + 4 + ((seed * 23) % (BOTTOM - TOP - 8))

    # Snap to the snake grid
    food_x = (food_x // SNAKE_SIZE) * SNAKE_SIZE
    food_y = (food_y // SNAKE_SIZE) * SNAKE_SIZE

    # Make sure food isn't inside the snake
    for segment in snake:

        if segment[0] == food_x and segment[1] == food_y:

            food_x += SNAKE_SIZE

            if food_x + SNAKE_SIZE > WIDTH - 1:
                food_x = 4

            break


# -------------------------------------------------
# START / RESET
# -------------------------------------------------

def start_game():

    global snake
    global direction
    global next_direction
    global score
    global game_state

    score = 0

    snake = [
        [60, 32],
        [56, 32],
        [52, 32],
        [48, 32]
    ]

    direction = (1, 0)
    next_direction = (1, 0)

    place_food()

    game_state = PLAYING


def reset_game():

    global game_state

    game_state = TITLE


# -------------------------------------------------
# DIRECTION
# -------------------------------------------------

def update_direction():

    global next_direction

    dx, dy = read_joystick()

    # Ignore diagonal input.
    # This makes the controls easier to use.

    if dx != 0:

        if dx == -1 and direction != (1, 0):
            next_direction = (-1, 0)

        elif dx == 1 and direction != (-1, 0):
            next_direction = (1, 0)

    elif dy != 0:

        if dy == -1 and direction != (0, 1):
            next_direction = (0, -1)

        elif dy == 1 and direction != (0, -1):
            next_direction = (0, 1)


# -------------------------------------------------
# SNAKE UPDATE
# -------------------------------------------------

def update_snake():

    global direction
    global snake
    global score
    global game_state

    direction = next_direction

    head_x = snake[0][0]
    head_y = snake[0][1]

    new_x = head_x + direction[0] * SNAKE_SIZE
    new_y = head_y + direction[1] * SNAKE_SIZE

    # Wall collision

    if new_x < 1:
        game_state = GAME_OVER
        return

    if new_x + SNAKE_SIZE > WIDTH - 1:
        game_state = GAME_OVER
        return

    if new_y < TOP:
        game_state = GAME_OVER
        return

    if new_y + SNAKE_SIZE > BOTTOM:
        game_state = GAME_OVER
        return

    # Self collision

    for segment in snake:

        if segment[0] == new_x and segment[1] == new_y:
            game_state = GAME_OVER
            return

    # Add new head

    new_head = [new_x, new_y]

    snake.insert(0, new_head)

    # Food collision

    if (
        new_x == food_x and
        new_y == food_y
    ):

        score += 1

        place_food()

    else:

        # Remove tail

        snake.pop()


# -------------------------------------------------
# DRAWING
# -------------------------------------------------

def draw_snake():

    for segment in snake:

        oled.fill_rect(
            segment[0],
            segment[1],
            SNAKE_SIZE,
            SNAKE_SIZE,
            1
        )


def draw_food():

    oled.fill_rect(
        food_x,
        food_y,
        SNAKE_SIZE,
        SNAKE_SIZE,
        1
    )


def draw_game():

    clear()

    oled.rect(0, TOP - 1, WIDTH, BOTTOM - TOP + 2, 1)   # border

    oled.text(
        "SCORE:" + str(score),
        0,
        0
    )

    draw_snake()
    draw_food()

    oled.show()


# -------------------------------------------------
# TITLE SCREEN
# -------------------------------------------------

def draw_title():

    clear()

    text_center(
        "SNAKE",
        15
    )

    text_center(
        "Press Joystick",
        32
    )

    text_center(
        "A = HOME",
        48
    )

    oled.show()


# -------------------------------------------------
# GAME OVER
# -------------------------------------------------

def draw_game_over():

    clear()

    text_center(
        "GAME OVER",
        15
    )

    text_center(
        "SCORE: " + str(score),
        30
    )

    text_center(
        "Press Joystick",
        46
    )

    oled.show()


# -------------------------------------------------
# TITLE HANDLER
# -------------------------------------------------

def handle_title():

    if joystick_pressed():
        start_game()


# -------------------------------------------------
# GAME OVER HANDLER
# -------------------------------------------------

def handle_game_over():

    if joystick_pressed():
        start_game()


# -------------------------------------------------
# MAIN GAME FUNCTION
# -------------------------------------------------

def run(o, jx, jy, js, hb):

    global game_state

    initialize(
        o,
        jx,
        jy,
        js,
        hb
    )

    game_state = TITLE

    last_state = -1

    while True:

        # GP21 immediately exits Snake

        if check_home():

            clear()
            oled.show()

            gc.collect()

            return

        # Draw screens only when state changes

        if game_state != last_state:

            if game_state == TITLE:
                draw_title()

            elif game_state == GAME_OVER:
                draw_game_over()

            last_state = game_state

        # Handle game

        if game_state == TITLE:

            handle_title()

        elif game_state == PLAYING:

            # Read joystick before moving
            update_direction()

            update_snake()

            if game_state == PLAYING:
                draw_game()

        elif game_state == GAME_OVER:

            handle_game_over()

        time.sleep_ms(FPS_DELAY)


JOYSTICK_CENTER = 32000