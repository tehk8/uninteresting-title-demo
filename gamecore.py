from axo import *
import random
DIRS={TK_UP:(0,-1),TK_DOWN:(0,1),TK_RIGHT:(1,0),TK_LEFT:(-1,0)}
ARROWS={i:DIRS[i] for i in DIRS}
DIRS[TK_H]=DIRS[TK_LEFT]
DIRS[TK_J]=DIRS[TK_DOWN]
DIRS[TK_K]=DIRS[TK_UP]
DIRS[TK_L]=DIRS[TK_RIGHT]
LETTERS={i:chr(i-TK_A+ord('a')) for i in range(TK_A,TK_Z+1)}
LETTERS[TK_SPACE]=' '
LETTERS[TK_CONTROL]='_'
NUMBERS={"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"zero":0}
def gc_collide(x1,y1,w1,h1,x2,y2,w2,h2):
    return x1<x2+w2 and x1+w1>x2 and y1<y2+h2 and y1+h1>y2
class TangibleObject(GameObject):
    def __init__(self,room,x,y,displaystr,blocking,size=(1,1),**kwargs):
        GameObject.__init__(self,room,x,y,displaystr,**kwargs)
        self.blocking=blocking
        self.size=size
        self.is_trigger=False
        self.is_interact=False
        self.trigger=None
        self.interact=None
    def collide(self,obj):
        x1,y1,x2,y2=self.x,self.y,obj.x,obj.y
        w1,h1=self.size
        w2,h2=obj.size
        return gc_collide(x1,y1,w1,h1,x2,y2,w2,h2)
    def move(self,dx,dy):
        x1,y1=self.x+dx,self.y+dy
        w1,h1=self.size
        w,h=self.game.size
        if x1<0 or y1<0 or x1+w1>w or y1+h1>h:
            return False
        objs=self.room.objects
        for o_id in objs:
            obj=objs[o_id]
            w2,h2=obj.size
            if obj.blocking and gc_collide(x1,y1,w1,h1,obj.x,obj.y,w2,h2):
                return False
        self.x=x1
        self.y=y1
        return True
    def set_trigger(self,trigger):
        self.is_trigger=True
        self.trigger=trigger
    def unset_trigger(self):
        self.is_trigger=False
        self.trigger=None
    def set_interact(self,interact):
        self.is_interact=True
        self.interact=interact
    def unset_interact(self,interact):
        self.is_interact=False
        self.interact=None
    def display(self):
        c=self.char
        if len(c)>1:
            return c
        w,h=self.size
        return "\n".join(h*[w*c])
class Player(TangibleObject):
    def __init__(self,room,x,y,**kwargs):
        TangibleObject.__init__(self,room,x,y,"@",False,color="green",**kwargs)
class TriggerObject(TangibleObject):
    def __init__(self,room,x,y,displaystr,trigger,**kwargs):
        TangibleObject.__init__(self,room,x,y,displaystr,False,**kwargs)
        self.set_trigger(trigger)
class InteractObject(TangibleObject):
    def __init__(self,room,x,y,displaystr,interaction,**kwargs):
        TangibleObject.__init__(self,room,x,y,displaystr,True,**kwargs)
        self.set_interact(interaction)
def gc_describe(s):
    def f(r):
        random.seed(random.randint(1,1000))
        d=random.choice(s)
        r.dialog("",d)
    return f
class DescribeObject(InteractObject):
    def __init__(self,room,x,y,displaystr,texts,**kwargs):
        InteractObject.__init__(self,room,x,y,displaystr,gc_describe(texts),**kwargs)
class Wall(DescribeObject):
    def __init__(self,room,x1,y1,x2,y2,**kwargs):
        texts=["It's a wall.","I like walls.","A wall.","Yet another wall.","Wall wall wall wall wall wall wall wall wall.\nWalllllllllllllllllllllllllllllll.","Why, just why.","The Great [color=red]Wall[/color]."]
        DescribeObject.__init__(self,room,x1,y1,"#",texts,size=(x2-x1+1,y2-y1+1),**kwargs)
class TextObject(TangibleObject):
    def __init__(self,room,x,y,text,**kwargs):
        t=text.split("\n")
        w,h=max([len(i) for i in t]),len(t)
        TangibleObject.__init__(self,room,x,y,text,False,size=(w,h),**kwargs)
def gc_door_goto(room_id):
    def t(r):
        return r.goto(room_id)
    return t
class Door(TriggerObject):
    def __init__(self,room,x,y,target,**kwargs):
        TriggerObject.__init__(self,room,x,y,"$",gc_door_goto(target),**kwargs)
        self.set_interact(gc_describe(["A door.\nIt probably leads somewhere."]))
def gc_trigger_emit(e):
    def f(r):
        return r.emit(e)
    return f
class ETriggerObject(TriggerObject):
    def __init__(self,room,x,y,displaystr,event,**kwargs):
        TriggerObject.__init__(self,room,x,y,displaystr,gc_trigger_emit(event),**kwargs)
class EInteractObject(InteractObject):
    def __init__(self,room,x,y,displaystr,event,**kwargs):
        InteractObject.__init__(self,room,x,y,displaystr,gc_trigger_emit(event),**kwargs)

class TerminalObject(TangibleObject):
    def __init__(self,room,size,layer=1):
        TangibleObject.__init__(self,room,0,0,"",False,size=size,layer=layer)
        w,h=size
        self.chars=[w*[" "] for i in range(h)]
    def readline(self,line):
        l=self.chars[line][:]
        while len(l) and l[-1]==" ": l.pop()
        return "".join(l)
    def display(self):
        return "\n".join(["".join(i) for i in self.chars])
    def printf(self,text):
        cur=self.room.cursor
        row,col=cur.y,cur.x
        t=text.split("\n")
        t.reverse()
        w,h=self.size
        while t:
            l=t.pop()
            if len(l)>w:
                t.append(l[w-1:])
                t.append(l[:w-1]+"-")
            else:
                if row==h:
                    self.room.dialog("","Press space to continue.")
                    self.clear()
                    row=0
                self.chars[row]=list(l)+(w-len(l))*[' ']
                row+=1
        cur.x=0
        cur.y=min(row,h-1)
        self.room.refresh()
    def clear(self):
        w,h=self.size
        self.chars=[w*[" "] for i in range(h)]
        cur=self.room.cursor
        cur.x=0
        cur.y=0
        self.room.refresh()
    def clearline(self):
        w,h=self.size
        self.chars[self.room.cursor.y]=w*[" "]
        self.room.refresh()
class Cursor(TangibleObject):
    def __init__(self,room,x,y,layer=0,**kwargs):
        TangibleObject.__init__(self,room,x,y,"\u2588",False,color="green",layer=layer,**kwargs)

def gc_letter(r,k):
    l=LETTERS[k]
    c=r.cursor
    row,col=c.y,c.x
    r.terminal.chars[row][col]=l
    c.move(1,0)
def gc_sendline(r,k):
    row=r.cursor.y
    l=r.terminal.readline(row)
    l=l.split(" ")
    cur=r.cursor
    if cur.y!=r.game.size[1]-1:
        cur.x=0
        cur.y+=1
    return r.run(l[0],l[1:])
def gc_escape(r,k):
    return r.goto(r.room)


class TangibleRoom(Room):
    def __init__(self,init,game,terminal="terminal"):
        Room.__init__(self,init,game)
        self.triggers={}
        self.interactions={}
        self.terminal_room=terminal
    def trigger(self,pos):
        objs=self.objects_at(pos)
        for ob_id in objs:
            o=objs[ob_id]
            if o.is_trigger:
                return o.trigger(self)
    def interact(self,pos):
        objs=self.objects_at(pos)
        for ob_id in objs:
            o=objs[ob_id]
            if o.is_interact:
                return o.interact(self)
    def objects_at(self,pos):
        x,y=pos
        objs_here={}
        objs=self.objects
        for ob_id in objs:
            o=objs[ob_id]
            if gc_collide(x,y,1,1,o.x,o.y,*o.size):
                objs_here[ob_id]=o
        return objs_here
    @property
    def player(self):
        return self.objects.get("player")
class TerminalRoom(TangibleRoom): #Terminal room represents the terminal mode in the code, while it's programmed as a room it is seen as a special mode in-game.
    def __init__(self,init,room,size,**kwargs):
        TangibleRoom.__init__(self,init,room,**kwargs)
        self.size=size
        self.commands={}
    @property
    def room(self):
        return self.get("room")
    @property
    def terminal(self):
        return self.objects.get("terminal")
    @property
    def cursor(self):
        return self.objects.get("cursor")
    def run(self,cmd,args):
        if cmd in self.commands:
            return self.commands[cmd](self,args)
    def command(self,cmd):
        def decorator(f):
            self.commands[cmd]=f
            return f
        return decorator
class TangibleGame(Game):
    def __init__(self,*args,**kwargs):
        Game.__init__(self,*args,**kwargs)
    def room(self,room_id,**kwargs):
        def decorator(init):
            r=TangibleRoom(init,self,**kwargs)
            self.rooms[room_id]=r
            for i in DIRS:
                r.key(i)(gc_arrow)
            r.key(TK_CLOSE)(lambda r,k: QUIT)
            r.key(TK_SPACE)(gc_interact)
            r.key(TK_T)(gc_terminal)
            return r
        return decorator
    def termroom(self,room_id,size,**kwargs):
        def decorator(init):
            def newinit(r):
                w=r.size
                h=r.game.size[1]
                r.command("debug")(gc_debug)
                r.command("/get")(gc_debug_get)
                r.command("/set")(gc_debug_set)
                r.command("/quit")(gc_debug_stop)
                r.command("/exit")(gc_debug_stop)
                r.command("/stop")(gc_debug_stop)
                r.add_object("terminal",TerminalObject,(w,h))
                r.add_object("cursor",Cursor,0,0)
                r.add_object("wall",Wall,w,0,w,h-1,color="red")
                return init(r)
            r=TerminalRoom(newinit,self,size,**kwargs)
            r.key(TK_ESCAPE)(gc_escape)
            r.key(TK_ENTER)(gc_sendline)
            r.key(TK_CLOSE)(lambda r,k: QUIT)
            r.key(TK_BACKSPACE)(gc_backspace)
            for k in LETTERS:
                r.key(k)(gc_letter)
            for i in ARROWS:
                r.key(i)(gc_arrow_term)
            self.rooms[room_id]=r
            return r
        return decorator
def gc_arrow(r,k):
    dx,dy=DIRS[k]
    p=r.player
    if not p: return
    if not p.move(dx,dy): return
    pos=p.x,p.y
    r.refresh()
    return r.trigger(pos)
def gc_interact(r,k):
    if not r.player: return
    oldc=r.player.color
    r.player.color="yellow"
    r.refresh()
    key=0
    keys=[i for i in DIRS]+[TK_ESCAPE]
    while not (key in keys):
        key=terminal.read()
    r.player.color=oldc
    r.refresh()
    if key in DIRS:
        dx,dy=DIRS[key]
        x,y=r.player.x+dx,r.player.y+dy
        action=r.interact((x,y))
    else:
        action=None
    return action
def gc_arrow_term(r,k):
    dx,dy=ARROWS[k]
    r.cursor.move(dx,dy)
def gc_backspace(r,k):
    cur=r.cursor
    cur.move(-1,0)
    r.terminal.chars[cur.y][cur.x]=" "
def gc_terminal(r,k):
    r.set("room",r.name)
    return r.goto(r.terminal_room)
def gc_condition(name):
    def decorator(f):
        def newf(r,*args,**kwargs):
            if r.get(name):
                return f(r,*args,**kwargs)
        return newf
    return decorator
@gc_condition("gc_debug")
def gc_debug(r,a):
    r.terminal.printf("/")
@gc_condition("gc_debug")
def gc_debug_get(r,a):
    if a:
        r.terminal.printf(r.get(a[0]).__str__())
@gc_condition("gc_debug")
def gc_debug_set(r,a):
    if len(a)>2:
        t=a[1]
        if t=="str":
            r.set(a[0]," ".join(a[2:]))
        elif t=="int":
            x=a[2:]
            result=0
            for i in x:
                if i.lower() not in NUMBERS:
                    r.terminal.printf(i+" is not a digit.")
                    return
                result=result*10+NUMBERS[i.lower()]
            r.set(a[0],result)
        elif t=="bool":
            if a[2].lower() in ["true","1","yes"]:
                r.set(a[0],True)
            elif a[2].lower() in ["false","0","no"]:
                r.set(a[0],False)
            else:
                r.terminal.printf(a[2]+" is not a boolean.")
                return
        else:
            r.terminal.printf(a[1]+" is not a known type, known types are str, int and bool.")
            return
        r.terminal.printf("Done.")
@gc_condition("gc_debug")
def gc_debug_stop(r,a):
    r.set("gc_debug",False)