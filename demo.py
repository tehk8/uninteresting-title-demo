#!/usr/bin/env python3
from gamecore import *
g=TangibleGame("Title (demo).",(80,25))
@g.room("room_begin")
def ro_beg(r):
    r.add_object("player",Player,40,13)
    r.add_object("wall1",Wall,0,0,39,0)
    r.add_object("wall2",Wall,41,0,80,0)
    r.add_object("door",Door,40,0,"room_other")
    r.add_object("button",EInteractObject,79,24,"+","open")
    if r.get("ro_beg_done"): return
    r.dialog("","Press space to get to next dialog.")
    r.dialog("","#s are walls, $s are doors.\nGo to the door please.")
    r.dialog("","Use the arrow keys (<v^>) or vi keys (hjkl) to move.")
    r.set("ro_beg_done",True)
@ro_beg.event("open")
def ro_beg_open(r):
    r.set("ro_oth_open",True)
    r.dialog("","Click!")
@g.room("room_other",terminal="term_oth")
def ro_oth(r):
    r.add_object("player",Player,40,23)
    r.add_object("door_beg",Door,40,24,"room_begin")
    hole="*"
    if r.get("ro_oth_open"):
        hole="O"
    r.add_object("hole_end",EInteractObject,0,0,hole,"end")
    if r.get("ro_oth_done"): return
    r.dialog("","Great!")
    r.dialog("","Press space, then an arrow key, to interact\n with an object directly in this direction.")
    r.dialog("","e.g. space+right = interact with the object directly at right.")
    r.dialog("","Find a way to open this hole now.")
    r.set("ro_oth_done",True)

@ro_oth.event("end")
def ro_oth_end(r):
    if not r.get("ro_oth_open"):
        r.dialog("","It's closed.")
    else:
        r.dialog("","Use the terminal to jump in the hole (press t).")
@g.room("room_end")
def ro_end(r):
    r.add_object("text",TextObject,0,13,"[* end happens *]\n\n:D")
    r.dialog("","...")
    return QUIT
@g.termroom("terminal",80)
def terminal(r):
    r.terminal.printf("Hello.\nPlease use the ESCAPE key to get out of there.\nNow.")
    r.commands["escape"]=lambda r,a: r.terminal.printf("No, I said *press* ESCAPE, not write ESCAPE.")
@terminal.command("setdebug")
def terminal_setdebug(r,a):
    r.set("gc_debug",True)
@g.termroom("term_oth",57)
def term_oth(r):
    if not r.get("ro_oth_open"):
        r.terminal.printf("The hole is still closed.\nGet out: press ESCAPE.")
        return
    r.add_object("hole",TextObject,58,13,"[* insert hole here *]")
    r.terminal.printf("The terminal lets you write commands.\nIts screen works like Commod*** **'s screen.\n(Name censored to avoid copyright strike, heh).\nPress enter on a line and it will send the entire\nline as a command.\nThe first word of the line (assuming it doesn't start\nwith a space) is the command and the other words are\narguments.\nYou can now read the dialog box and press space.")
    r.dialog("","Please read the content of the window below before pressing space.")
    r.dialog("","Ok, try the command \"jump\" (without quotes), it's only usable in this room.")
    r.dialog("|O=O|;","[[* Ok, I know I could have implemented the jump without using the terminal mode,\nbut I wanted a way to introduce this mode anyway. *]]")
@term_oth.command("jump")
@gc_condition("ro_oth_open")
def term_oth_jump(r,a):
    r.terminal.printf("You jumped in a hole.\nYou may now exit the terminal. Press ESCAPE.")
    r.set("room","room_end")
g.play("room_begin")