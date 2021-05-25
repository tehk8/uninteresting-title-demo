from bearlibterminal import terminal

GOTO=1
QUIT=2
EVENT=3
class Game:
    def __init__(self,title,size):
        self.title=title
        self.data={}
        self.rooms={}
        self.size=size
        self.next_room=None
    def room(self,room_id):
        def decorator(init):
            r=Room(init,self)
            self.rooms[room_id]=r
            return r
        return decorator
    def play(self,room_id):
        running=True
        self._current=room_id
        terminal.open()
        w,h=self.size
        w=max(w+2,87)
        h+=4
        terminal.set("window.title="+self.title)
        terminal.set("window.size="+str(w)+","+str(h))
        while running:
            room=self.rooms[self._current]
            action=room.mainloop()
            if action==QUIT:
                running=False
            elif action==GOTO:
                self._current=self.next_room
        terminal.close()

class Room:
    def __init__(self,init,game):
        self._init=init
        self.game=game
        self.objects={}
        self.handlers={}
        self.events={}
        self.next_event=None
    def key(self,key_id):
        def decorator(handler):
            self.handlers[key_id]=handler
            return handler
        return decorator
    def event(self,event_id):
        def decorator(e):
            self.events[event_id]=e
            return e
        return decorator
    def init(self):
        self.objects={}
        return self._init(self)
    def refresh(self):
        terminal.clear()
        w,h=self.game.size
        for obj_id in self.objects:
            o=self.objects[obj_id]
            terminal.layer(o.layer)
            terminal.color(o.color)
            spr=o.display()
            spr=spr.split("\n")
            for y in range(max(0,-o.y),len(spr)):
                for x in range(min(len(spr[y]),w-o.x)):
                    terminal.put(1+o.x+x,3+o.y+y,spr[y][x])
        terminal.layer(0)
        terminal.color("white")
        for i in range(h):
            terminal.put(0,3+i,"\u2502")
            terminal.put(w+1,3+i,"\u2502")
        terminal.printf(1,2,w*"\u2500")
        terminal.printf(1,3+h,w*"\u2500")
        terminal.put(0,2,"\u250c")
        terminal.put(0,3+h,"\u2514")
        terminal.put(w+1,3+h,"\u2518")
        terminal.put(w+1,2,"\u2510")
        terminal.refresh()
    def dialog(self,head,text,hcol="white",tcol="white"):
        self.refresh()
        terminal.layer(0)
        terminal.color(hcol)
        terminal.printf(0,0,head[:7])
        t=text.split("\n")
        terminal.color(tcol)
        terminal.printf(7,0,t[0][:80])
        if len(t)>1:
            terminal.printf(7,1,t[1][:80])
        terminal.refresh()
        while terminal.read()!=terminal.TK_SPACE:
            pass
        terminal.printf(0,0,87*" ")
        terminal.printf(0,1,87*" ")
        terminal.refresh()
    def set(self,var,value):
        self.game.data[var]=value
    def get(self,var):
        return self.game.data.get(var)
    def goto(self,room_id):
        self.game.next_room=room_id
        return GOTO
    def emit(self,event_id):
        self.next_event=event_id
        return EVENT
    def add_object(self,name,Obj,*args,**kwargs):
        self.objects[name]=Obj(self,*args,**kwargs)
    def mainloop(self):
        self.refresh()
        action=self.init()
        while True:
            self.refresh()
            while action:
                if action in [GOTO,QUIT]:
                    return action
                elif action==EVENT:
                    ev_id=self.next_event
                    event=self.events[ev_id]
                    action=event(self)
                self.refresh()
            key=terminal.read()
            hndl=self.handlers.get(key)
            if hndl:
                action=hndl(self,key)
    @property
    def name(self):
        return self.game._current

class GameObject:
    def __init__(self,room,x,y,displaystr,color="white",layer=0):
        self.x=x
        self.y=y
        self.room=room
        self.char=displaystr
        self.color=color
        self.layer=layer
        self.game=room.game
    def display(self):
        return self.char
