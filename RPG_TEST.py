# ------------------------------
# Tactical RPG: Overworld + Battle + Ice Spell + Auto-Save
# Freezing skips turn
# Compatible with Python 3.13.5 IDLE
# ------------------------------

import turtle
import random
import time
import os

# ------------------------------
# SETTINGS
# ------------------------------
GRID_SIZE = 6
CELL_SIZE = 100
ANIMATION_SPEED = 0.05
MAP_SIZE = 10
OVERWORLD_CELL = 60

# ------------------------------
# SCREEN SETUP
# ------------------------------
screen = turtle.Screen()
screen.title("Tactical RPG – Overworld & Battle")
screen.bgcolor("lightblue")
screen.setup(width=1200, height=900)

# ------------------------------
# GLOBAL VARIABLES
# ------------------------------
battle_mode = False
heroes = []
enemies = []
characters = []
turn_index = 0
current_skill = "basic"
selected_target_tile = None
selecting_spell_target = False
player_pos = [0, 0]  # Overworld coordinates

save_file = "save.txt"

# ------------------------------
# TURTLE OBJECTS
# ------------------------------
# Draw overworld map
overworld_map = []
for y in range(MAP_SIZE):
    row=[]
    for x in range(MAP_SIZE):
        # Simple terrain assignment
        terrain=random.choice(["green","green","green","blue","gray"])
        row.append(terrain)
        drawer.goto(-MAP_SIZE*OVERWORLD_CELL//2 + x*OVERWORLD_CELL,
                    -MAP_SIZE*OVERWORLD_CELL//2 + y*OVERWORLD_CELL)
        drawer.fillcolor(terrain)
        drawer.begin_fill()
        for _ in range(4):
            drawer.forward(OVERWORLD_CELL)
            drawer.left(90)
        drawer.end_fill()
    overworld_map.append(row)

# Player turtle
player = turtle.Turtle()
player.shape("circle")
player.color("yellow")
player.penup()
player.goto(-MAP_SIZE*OVERWORLD_CELL//2 + player_pos[0]*OVERWORLD_CELL + OVERWORLD_CELL//2,
            -MAP_SIZE*OVERWORLD_CELL//2 + player_pos[1]*OVERWORLD_CELL + OVERWORLD_CELL//2)

drawer = turtle.Turtle()
drawer.hideturtle()
drawer.speed(0)
drawer.penup()

effect = turtle.Turtle()
effect.hideturtle()
effect.penup()

highlighter = turtle.Turtle()
highlighter.hideturtle()
highlighter.speed(0)
highlighter.penup()

stun_icon = turtle.Turtle()
stun_icon.hideturtle()
stun_icon.penup()
stun_icon.shape("circle")
stun_icon.color("gold")

turn_display = turtle.Turtle()
turn_display.hideturtle()
turn_display.penup()
turn_display.goto(0, 300)

highlighted_squares = []

# ------------------------------
# CHARACTER CLASS
# ------------------------------
class Character:
    def __init__(self,name,x,y,color,hp=25):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.hp = hp
        self.max_hp = hp
        self.level = 1
        self.xp = 0
        self.turtle = turtle.Turtle()
        self.turtle.shape("circle")
        self.turtle.color(color)
        self.turtle.penup()
        self.hp_bar = turtle.Turtle()
        self.hp_bar.hideturtle()
        self.hp_bar.penup()
        self.status_label = turtle.Turtle()
        self.status_label.hideturtle()
        self.status_label.penup()
        self.status_effects = {}
        self.cooldowns = {"strong":0,"fireball":0,"lightning":0,"heal":0,"ice":0}
        self.update_position()
        self.update_hp_bar()
        self.update_status_label()

    def update_position(self):
        if battle_mode:
            screen_x = -GRID_SIZE*CELL_SIZE//2 + self.x*CELL_SIZE + CELL_SIZE//2
            screen_y = -GRID_SIZE*CELL_SIZE//2 + self.y*CELL_SIZE + CELL_SIZE//2
        else:
            screen_x = -MAP_SIZE*OVERWORLD_CELL//2 + self.x*OVERWORLD_CELL + OVERWORLD_CELL//2
            screen_y = -MAP_SIZE*OVERWORLD_CELL//2 + self.y*OVERWORLD_CELL + OVERWORLD_CELL//2
        self.turtle.goto(screen_x,screen_y)
        self.update_hp_bar()
        self.update_status_label()

    def update_hp_bar(self):
        self.hp_bar.clear()
        if not battle_mode: return
        self.hp_bar.goto(self.turtle.xcor()-20, self.turtle.ycor()+30)
        self.hp_bar.color("red")
        self.hp_bar.pendown()
        ratio = max(0,self.hp)/self.max_hp
        self.hp_bar.forward(40*ratio)
        self.hp_bar.penup()

    def update_status_label(self):
        self.status_label.clear()
        if not self.status_effects or not battle_mode: return
        txt = " ".join([f"{k}({v})" for k,v in self.status_effects.items()])
        self.status_label.goto(self.turtle.xcor(), self.turtle.ycor()+45)
        self.status_label.write(txt, align="center", font=("Arial",9,"normal"))

    def animate_move(self,target_x,target_y):
        steps = max(abs(target_x-self.x),abs(target_y-self.y))
        if steps == 0: return
        for step in range(1,steps+1):
            new_x = self.x + (target_x-self.x)*step/steps
            new_y = self.y + (target_y-self.y)*step/steps
            self.turtle.goto(-GRID_SIZE*CELL_SIZE//2 + new_x*CELL_SIZE + CELL_SIZE//2,
                             -GRID_SIZE*CELL_SIZE//2 + new_y*CELL_SIZE + CELL_SIZE//2)
            screen.update()
            time.sleep(ANIMATION_SPEED)
        self.x = target_x
        self.y = target_y
        self.update_position()

    def apply_status_start_turn(self):
        stunned = False
        # Freezing acts like Stun
        if "Freezing" in self.status_effects:
            stunned=True
            del self.status_effects["Freezing"]
        for k in list(self.status_effects.keys()):
            self.status_effects[k]-=1
            if k=="Shock":
                self.hp-=2
                show_effect(self.x,self.y,"yellow",28)
            elif k=="Burn":
                self.hp-=1
                show_effect(self.x,self.y,"red",24)
            elif k=="Regen":
                self.hp=min(self.max_hp,self.hp+2)
                show_effect(self.x,self.y,"green",24)
            elif k=="Stun":
                stunned=True
                stun_icon.goto(self.turtle.xcor(),self.turtle.ycor()+60)
                stun_icon.showturtle()
            if self.status_effects[k]<=0:
                del self.status_effects[k]
        if "Stun" not in self.status_effects:
            stun_icon.hideturtle()
        if self.hp<0: self.hp=0
        self.update_hp_bar()
        self.update_status_label()
        return stunned

    def attack(self,target,skill="basic"):
        if skill in self.cooldowns and self.cooldowns[skill]>0:
            print(f"{skill} cooldown {self.cooldowns[skill]}")
            return False
        used=False
        if skill=="basic" and target:
            if abs(self.x-target.x)<=1 and abs(self.y-target.y)<=1:
                target.hp-=random.randint(2,4)
                show_effect(target.x,target.y,"orange",28)
                used=True
        elif skill=="strong" and target:
            if abs(self.x-target.x)<=1 and abs(self.y-target.y)<=1:
                target.hp-=random.randint(4,6)
                show_effect(target.x,target.y,"red",36)
                self.cooldowns["strong"]=3
                used=True
        elif skill=="fireball" and target:
            print(f"{self.name} casts Fireball!")
            for e in enemies:
                if abs(e.x-target.x)<=1 and abs(e.y-target.y)<=1:
                    e.hp-=random.randint(3,5)
                    e.status_effects["Burn"]=2
                    show_effect(e.x,e.y,"purple",40)
                    e.update_hp_bar()
            self.cooldowns["fireball"]=3
            used=True
        elif skill=="lightning" and target:
            print(f"{self.name} casts Lightning!")
            for e in enemies:
                if abs(e.x-target.x)<=1 and abs(e.y-target.y)<=1:
                    e.hp-=random.randint(4,6)
                    e.status_effects["Shock"]=2
                    if random.random()<0.3: e.status_effects["Stun"]=1
                    show_effect(e.x,e.y,"yellow",44)
                    e.update_hp_bar()
            self.cooldowns["lightning"]=4
            used=True
        elif skill=="heal":
            self.hp=min(self.max_hp,self.hp+random.randint(5,8))
            self.status_effects["Regen"]=2
            show_effect(self.x,self.y,"green",40)
            self.cooldowns["heal"]=3
            used=True
        elif skill=="ice" and target:
            print(f"{self.name} casts Ice Blast!")
            for e in enemies:
                if abs(e.x-target.x)<=1 and abs(e.y-target.y)<=1:
                    e.hp-=random.randint(3,5)
                    e.status_effects["Freezing"]=1
                    show_effect(e.x,e.y,"cyan",40)
                    e.update_hp_bar()
            self.cooldowns["ice"]=4
            used=True
        if used:
            self.update_hp_bar()
            self.update_status_label()
        return used

    def reduce_cooldowns(self):
        for k in self.cooldowns:
            if self.cooldowns[k]>0:
                self.cooldowns[k]-=1

# ------------------------------
# EFFECT
# ------------------------------
def show_effect(x,y,color="orange",size=40,pause=0.12):
    effect.goto(-GRID_SIZE*CELL_SIZE//2 + x*CELL_SIZE + CELL_SIZE//2,
                -GRID_SIZE*CELL_SIZE//2 + y*CELL_SIZE + CELL_SIZE//2)
    effect.color(color)
    effect.dot(size)
    screen.update()
    time.sleep(pause)
    effect.clear()

# ------------------------------
# HIGHLIGHT
# ------------------------------
def highlight_range(character,rng=1):
    highlighter.clear()
    highlighted_squares.clear()
    for dx in range(-rng,rng+1):
        for dy in range(-rng,rng+1):
            x=character.x+dx
            y=character.y+dy
            if 0<=x<GRID_SIZE and 0<=y<GRID_SIZE:
                highlighter.goto(-GRID_SIZE*CELL_SIZE//2 + x*CELL_SIZE, -GRID_SIZE*CELL_SIZE//2 + y*CELL_SIZE)
                highlighter.stamp()
                highlighted_squares.append((x,y))

def highlight_spell_tile(tile,color):
    x,y=tile
    highlighter.color(color)
    highlighter.goto(-GRID_SIZE*CELL_SIZE//2 + x*CELL_SIZE, -GRID_SIZE*CELL_SIZE//2 + y*CELL_SIZE)
    highlighter.stamp()
    screen.update()
    time.sleep(0.15)
    highlighter.clear()

# ------------------------------
# TURN DISPLAY
# ------------------------------
def update_turn_display():
    turn_display.clear()
    if not characters: return
    c = characters[turn_index]
    txt = f"{c.name}'s Turn"
    if c in heroes:
        txt+= f" Skill: {current_skill}"
    turn_display.write(txt, align="center", font=("Arial",16,"bold"))

# ------------------------------
# CLEANUP AND END CHECK
# ------------------------------
def cleanup_dead():
    global enemies, characters
    enemies=[e for e in enemies if e.hp>0]
    characters=[c for c in characters if c.hp>0]

def check_battle_end():
    if not enemies:
        turn_display.clear()
        turn_display.write("Victory!", align="center", font=("Arial",24,"bold"))
        print("Victory!")
        auto_save()
        return True
    if not any(h.hp>0 for h in heroes):
        turn_display.clear()
        turn_display.write("Defeat...", align="center", font=("Arial",24,"bold"))
        print("Defeat...")
        return True
    return False

# ------------------------------
# AUTO SAVE / LOAD
# ------------------------------
def auto_save():
    data=[]
    for h in heroes:
        data.append(f"{h.name},{h.x},{h.y},{h.hp},{h.max_hp},{h.level},{h.xp}")
    data.append(f"{player_pos[0]},{player_pos[1]}")
    with open(save_file,"w") as f:
        f.write("\n".join(data))
    print("Game auto-saved!")

def auto_load():
    global heroes, player_pos
    if not os.path.exists(save_file): return
    res=screen.textinput("Load Game?","Save found. Load? (y/n)")
    if res and res.lower()=="y":
        with open(save_file,"r") as f:
            lines=f.read().splitlines()
        for i,h in enumerate(heroes):
            info=lines[i].split(",")
            h.x=int(info[1])
            h.y=int(info[2])
            h.hp=int(info[3])
            h.max_hp=int(info[4])
            h.level=int(info[5])
            h.xp=int(info[6])
            h.update_position()
        px,py=lines[-1].split(",")
        player_pos[0]=int(px)
        player_pos[1]=int(py)
        print("Game loaded!")

# ------------------------------
# ENEMY AI
# ------------------------------
def enemy_ai(enemy):
    if not heroes: return
    target=min([h for h in heroes if h.hp>0], key=lambda h: abs(h.x-enemy.x)+abs(h.y-enemy.y))
    if abs(enemy.x-target.x)>1:
        step_x=1 if target.x>enemy.x else -1
        enemy.animate_move(enemy.x+step_x,enemy.y)
    elif abs(enemy.y-target.y)>1:
        step_y=1 if target.y>enemy.y else -1
        enemy.animate_move(enemy.x,enemy.y+step_y)
    if abs(enemy.x-target.x)<=1 and abs(enemy.y-target.y)<=1:
        enemy.attack(target,"basic")

# ------------------------------
# TURN LOGIC
# ------------------------------
def next_turn():
    global turn_index
    cleanup_dead()
    if check_battle_end(): return
    turn_index=(turn_index+1)%len(characters)
    unit=characters[turn_index]
    stunned=unit.apply_status_start_turn()
    cleanup_dead()
    if check_battle_end(): return
    if stunned:
        unit.reduce_cooldowns()
        next_turn()
        return
    update_turn_display()
    if unit in heroes:
        highlight_range(unit)
    else:
        enemy_ai(unit)
        unit.reduce_cooldowns()
        next_turn()

# ------------------------------
# PLAYER ACTIONS
# ------------------------------
def on_click(x,y):
    global selecting_spell_target, selected_target_tile
    if not characters or check_battle_end(): return
    c = characters[turn_index]
    if c not in heroes: return
    gx=int((x+GRID_SIZE*CELL_SIZE/2)//CELL_SIZE)
    gy=int((y+GRID_SIZE*CELL_SIZE/2)//CELL_SIZE)
    if selecting_spell_target:
        selected_target_tile=(gx,gy)
        color = "red" if current_skill=="fireball" else "yellow" if current_skill=="lightning" else "cyan"
        highlight_spell_tile(selected_target_tile,color)
        selecting_spell_target=False
        player_use_skill()
        return
    if (gx,gy) in highlighted_squares:
        c.animate_move(gx,gy)
        highlight_range(c)

def player_use_skill():
    global current_skill, selecting_spell_target, selected_target_tile
    c=characters[turn_index]
    if current_skill in ("fireball","lightning","ice") and not selected_target_tile:
        print("Click a tile to target your spell.")
        selecting_spell_target=True
        return
    target=None
    if current_skill in ("basic","strong"):
        for e in enemies:
            if abs(c.x-e.x)<=1 and abs(c.y-e.y)<=1:
                target=e
                break
    elif selected_target_tile:
        gx,gy=selected_target_tile
        dummy=type("Dummy",(),{"x":gx,"y":gy})
        target=dummy
    used=c.attack(target,current_skill)
    selected_target_tile=None
    selecting_spell_target=False
    if used:
        c.reduce_cooldowns()
        next_turn()

def end_turn():
    c=characters[turn_index]
    c.reduce_cooldowns()
    next_turn()

def set_skill(s):
    global current_skill
    current_skill=s
    update_turn_display()

def move_player(dx,dy):
    new_x = player_pos[0]+dx
    new_y = player_pos[1]+dy
    if 0<=new_x<MAP_SIZE and 0<=new_y<MAP_SIZE:
        if overworld_map[new_y][new_x]!="gray":  # can't walk into mountains
            player_pos[0]=new_x
            player_pos[1]=new_y
            player.goto(-MAP_SIZE*OVERWORLD_CELL//2 + new_x*OVERWORLD_CELL + OVERWORLD_CELL//2,
                        -MAP_SIZE*OVERWORLD_CELL//2 + new_y*OVERWORLD_CELL + OVERWORLD_CELL//2)

screen.onkey(lambda:move_player(0,1),"Up")
screen.onkey(lambda:move_player(0,-1),"Down")
screen.onkey(lambda:move_player(-1,0),"Left")
screen.onkey(lambda:move_player(1,0),"Right")
screen.listen()

# ------------------------------
# KEY BINDINGS
# ------------------------------
screen.listen()
screen.onkey(lambda:set_skill("basic"),"b")
screen.onkey(lambda:set_skill("strong"),"s")
screen.onkey(lambda:set_skill("fireball"),"f")
screen.onkey(lambda:set_skill("lightning"),"l")
screen.onkey(lambda:set_skill("heal"),"h")
screen.onkey(lambda:set_skill("ice"),"i")
screen.onkey(player_use_skill,"Return")
screen.onkey(end_turn,"e")
screen.onclick(on_click)

# ------------------------------
# INIT HEROES
# ------------------------------
hero=Character("Hero",0,0,"green",hp=30)
mage=Character("Mage",0,1,"blue",hp=26)
cleric=Character("Cleric",1,0,"cyan",hp=28)
heroes=[hero,mage,cleric]

# ------------------------------
# TEST ENEMIES
# ------------------------------
e1=Character("Slime",5,5,"darkred",hp=12)
e2=Character("Goblin",4,4,"red",hp=14)
enemies=[e1,e2]
characters=heroes+enemies

# ------------------------------
# START GAME
# ------------------------------
auto_load()
update_turn_display()
highlight_range(heroes[0])
print("Controls:")
print("Click yellow squares to move.")
print("b,s,f,l,h,i = choose skill")
print("Enter = use skill")
print("e = end turn")
turtle.done()
