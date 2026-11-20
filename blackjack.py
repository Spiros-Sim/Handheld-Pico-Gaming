import time
import random
import gc

WIDTH=128
HEIGHT=64

JOYSTICK_CENTER=32500
JOYSTICK_DEADZONE=6000
BUTTON_DEBOUNCE=200

v="A23456789TJQK"

oled=None
joystick_x=None
joystick_y=None
joystick_sw=None
home_button=None

button_last=1
button_time=0

wins=0


def val(h):
    s=0
    a=0
    for c in h:
        if c=="A":
            s+=1
            a+=1
        elif c in "TJQK":
            s+=10
        else:
            s+=int(c)
    while a and s+10<=21:
        s+=10
        a-=1
    return s


def shuffle(d):
    for i in range(len(d)-1,0,-1):
        j=random.getrandbits(16)%(i+1)
        d[i],d[j]=d[j],d[i]


def clear():
    oled.fill(0)


def center(t,y):
    x=(WIDTH-len(t)*8)//2
    if x<0:
        x=0
    oled.text(t,x,y)


def button_pressed():
    global button_last
    global button_time

    c=joystick_sw.value()

    if c==0 and button_last==1:
        n=time.ticks_ms()

        if time.ticks_diff(n,button_time)>BUTTON_DEBOUNCE:
            button_last=0
            button_time=n
            return True

    button_last=c
    return False


def home_pressed():
    if home_button.value()==0:
        time.sleep_ms(30)

        if home_button.value()==0:
            while home_button.value()==0:
                time.sleep_ms(10)
            return True

    return False


def draw_hand(label,h,y):
    oled.text(label,0,y)

    x=48

    for c in h:
        if x>112:
            x=48
            y+=9

        oled.text(c,x,y)
        x+=8

    oled.text(str(val(h)),0,y+9)


def draw_game(p,d,sel,result=""):

    clear()

    if result=="":
        oled.text("DEALER",0,0)

        x=56

        for c in d[:1]:
            oled.text(c,x,0)
            x+=10

        oled.text("??",x,0)

        oled.text("PLAYER",0,18)

        x=56
        y=18

        for c in p:
            if x>112:
                x=56
                y+=10

            oled.text(c,x,y)
            x+=10

        oled.text("TOTAL "+str(val(p)),0,38)
        oled.text("WINS:"+str(wins),72,38)

        if sel==0:
            oled.text(">HIT",20,54)
            oled.text(" STAND",72,54)
        else:
            oled.text(" HIT",20,54)
            oled.text(">STAND",72,54)

    else:
        oled.text("DEALER",0,0)

        x=56
        y=0

        for c in d:
            if x>112:
                x=56
                y+=10

            oled.text(c,x,y)
            x+=10

        oled.text("TOTAL "+str(val(d)),0,18)
        oled.text("WINS:"+str(wins),72,18)

        oled.text("PLAYER",0,30)

        x=56
        y=30

        for c in p:
            if x>112:
                x=56
                y+=10

            oled.text(c,x,y)
            x+=10

        oled.text("TOTAL "+str(val(p)),0,48)

        center(result,56)

    oled.show()


def move_selector(sel):

    z=joystick_x.read_u16()

    if z<JOYSTICK_CENTER-JOYSTICK_DEADZONE:
        return 0

    if z>JOYSTICK_CENTER+JOYSTICK_DEADZONE:
        return 1

    return sel


def wait_release():

    while joystick_sw.value()==0:
        time.sleep_ms(10)

    while home_button.value()==0:
        time.sleep_ms(10)


def round_game():

    global wins

    d=list(v)*4
    shuffle(d)

    p=[d.pop(),d.pop()]
    q=[d.pop(),d.pop()]

    sel=0

    draw_game(p,q,sel)

    while True:

        # A hand of 21 ends the turn automatically (no hitting)
        if val(p)==21:
            break

        if home_pressed():
            return None

        ns=move_selector(sel)

        if ns!=sel:
            sel=ns
            draw_game(p,q,sel)

        if button_pressed():

            wait_release()

            if sel==0:

                p.append(d.pop())

                if val(p)>=21:
                    break

                draw_game(p,q,sel)

            else:
                break

        time.sleep_ms(35)

    if val(p)>21:
        draw_game(p,q,sel,"BUST")
        time.sleep_ms(1500)
        return True

    while val(q)<17:

        q.append(d.pop())

        draw_game(p,q,sel)

        time.sleep_ms(400)

    pv=val(p)
    dv=val(q)

    if dv>21:
        result="YOU WIN"
    elif pv>dv:
        result="YOU WIN"
    elif pv<dv:
        result="DEALER WINS"
    else:
        result="PUSH"

    if result=="YOU WIN":
        wins+=1

    draw_game(p,q,sel,result)

    time.sleep_ms(1500)

    return True


def run(o,jx,jy,js,hb):

    global oled
    global joystick_x
    global joystick_y
    global joystick_sw
    global home_button
    global button_last
    global button_time
    global wins

    oled=o
    joystick_x=jx
    joystick_y=jy
    joystick_sw=js
    home_button=hb

    button_last=joystick_sw.value()
    button_time=time.ticks_ms()

    wins=0

    clear()

    center("BLACKJACK",18)
    center("PRESS JOYSTICK",34)
    center("A = HOME",50)

    oled.show()

    while joystick_sw.value()==0:
        time.sleep_ms(10)

    while True:

        if home_pressed():
            clear()
            oled.show()
            gc.collect()
            return

        if button_pressed():

            wait_release()

            result=round_game()

            if result is None:
                clear()
                oled.show()
                gc.collect()
                return

        time.sleep_ms(35)