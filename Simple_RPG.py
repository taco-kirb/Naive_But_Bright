import turtle
import random
import math

# ---------------------------
# Screen Setup
# ---------------------------
screen = turtle.Screen()
screen.title("Turn-Based RPG")
screen.bgcolor("lightblue")
screen.tracer(0)
screen.setup(width=1200, height=600)

# ---------------------------
# Character Class
# ---------------------------
class Character:
    def __init__(self, name, color, x, y, hp=100, attack=20, is_player=False):
        self.name = name
        self.color = color
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.status = None
        self.status_duration = 0
        self.special_cd = 0
        self.is_player = is_player
        self.active_particles = []
        self.particle_queue = []
        self.particle_running = False
        self.message_count = 0  # stacking messages
        self.status_cd = {"Burned":0, "Bleeding":0, "Shocked":0, "Frozen":0}

        self.turtle = turtle.Turtle()
        self.turtle.shape("turtle")
        self.turtle.color(color)
        self.turtle.penup()
        self.turtle.goto(x, y)

    def flash(self, color=None, duration=200):
        orig = self.turtle.color()[0]
        self.turtle.color(color if color else "white")
        screen.update()
        screen.ontimer(lambda: self.turtle.color(orig), duration)

    def move_toward(self, target_x, target_y, steps=10, callback=None):
        ox, oy = self.turtle.pos()
        dx = (target_x - ox) / steps
        dy = (target_y - oy) / steps
        step = 0
        def animate():
            nonlocal step
            if step < steps:
                self.turtle.goto(self.turtle.xcor()+dx, self.turtle.ycor()+dy)
                screen.update()
                step +=1
                screen.ontimer(animate,20)
            else:
                if callback:
                    callback()
        animate()

# ---------------------------
# Shake Animation
# ---------------------------
def shake_character(character, intensity=5, shakes=6, callback=None):
    ox, oy = character.turtle.pos()
    step = 0
    def do_shake():
        nonlocal step
        if step < shakes:
            dx = intensity if step%2==0 else -intensity
            character.turtle.goto(ox+dx, oy)
            screen.update()
            step +=1
            screen.ontimer(do_shake,30)
        else:
            character.turtle.goto(ox, oy)
            screen.update()
            if callback:
                callback()
    do_shake()

# ---------------------------
# Particle Effects
# ---------------------------
def particle_effect(character, count=10, distance=15, color="yellow", callback=None):
    character.particle_queue.append((count, distance, color, callback))
    if character.particle_running: return

    def run_next():
        if not character.particle_queue:
            character.particle_running = False
            return
        character.particle_running = True
        count, distance, color, callback_inner = character.particle_queue.pop(0)

        for p in character.active_particles:
            p.hideturtle()
            p.clear()
        character.active_particles.clear()

        particles = []
        for _ in range(count):
            p = turtle.Turtle()
            p.hideturtle()
            p.penup()
            p.shape("circle")
            p.color(color)
            p.shapesize(0.5,0.5)
            px, py = character.turtle.pos()
            p.goto(px, py)
            p.showturtle()
            particles.append(p)
            character.active_particles.append(p)

        steps = 6
        step = 0
        angles = [random.uniform(0,360) for _ in range(count)]
        def animate():
            nonlocal step
            if step < steps:
                for i,p in enumerate(particles):
                    rad = angles[i]*math.pi/180
                    dx = distance/steps*math.cos(rad)
                    dy = distance/steps*math.sin(rad)
                    p.goto(p.xcor()+dx, p.ycor()+dy)
                screen.update()
                step +=1
                screen.ontimer(animate,30)
            else:
                for p in particles:
                    p.hideturtle()
                    p.clear()
                character.active_particles.clear()
                if callback_inner:
                    callback_inner()
                run_next()
        animate()
    run_next()

# ---------------------------
# Floating Damage
# ---------------------------
def show_damage(target, dmg, crit=False, hit_num=1):
    dmg_turtle = turtle.Turtle()
    dmg_turtle.hideturtle()
    dmg_turtle.penup()
    dmg_turtle.color("yellow" if crit else "white")
    y_offset = 40 + (hit_num-1)*15
    dmg_turtle.goto(target.turtle.xcor(), target.turtle.ycor() + y_offset)
    dmg_turtle.write(str(dmg), align="center", font=("Arial", 14, "bold"))
    steps = 15
    step = 0
    def animate():
        nonlocal step
        if step < steps:
            x,y = dmg_turtle.pos()
            dmg_turtle.goto(x, y+2)
            step += 1
            screen.ontimer(animate, 30)
        else:
            dmg_turtle.clear()
            dmg_turtle.hideturtle()
    animate()

# ---------------------------
# Floating Status Message
# ---------------------------
def show_status_message(character, status_text, color="white", current_messages=0):
    msg_turtle = turtle.Turtle()
    msg_turtle.hideturtle()
    msg_turtle.penup()
    msg_turtle.color(color)
    y_offset = 50 + current_messages*15
    msg_turtle.goto(character.turtle.xcor(), character.turtle.ycor() + y_offset)
    msg_turtle.write(status_text, align="center", font=("Arial", 12, "bold"))
    steps=20
    step=0
    def animate():
        nonlocal step
        if step<steps:
            x,y=msg_turtle.pos()
            msg_turtle.goto(x, y+2)
            step+=1
            screen.ontimer(animate,30)
        else:
            msg_turtle.clear()
            msg_turtle.hideturtle()
    animate()

# ---------------------------
# Teams
# ---------------------------
players = [
    Character("Player","green",-400,0,hp=100,attack=20,is_player=True),
    Character("Ally1","blue",-400,100,hp=80,attack=15,is_player=True)
]
enemies = [
    Character("Enemy1","red",400,50,hp=80,attack=15),
    Character("Enemy2","orange",400,-50,hp=80,attack=15)
]

# ---------------------------
# Health Display
# ---------------------------
health_display = turtle.Turtle()
health_display.hideturtle()
health_display.penup()
health_display.goto(0,250)
def clamp_hp(c): c.hp=max(0,c.hp)
def update_health():
    health_display.clear()
    text=""
    for p in players:
        clamp_hp(p)
        text+=f"{p.name} HP: {p.hp} ({p.status if p.status else 'Normal'})  "
    text+="\n"
    for e in enemies:
        clamp_hp(e)
        text+=f"{e.name} HP: {e.hp} ({e.status if e.status else 'Normal'})  "
    health_display.write(text,align="center",font=("Arial",16,"bold"))

# ---------------------------
# Status Icons
# ---------------------------
status_turtles={}
def init_status_icons():
    for c in players+enemies:
        t=turtle.Turtle()
        t.hideturtle()
        t.penup()
        t.goto(c.turtle.xcor(), c.turtle.ycor()+40)
        status_turtles[c]=t
def update_status_icons():
    for c,t in status_turtles.items():
        t.clear()
        t.goto(c.turtle.xcor(), c.turtle.ycor()+40)
        if c.status is None or c.hp<=0:
            continue
        color_map={"Burned":"orange","Bleeding":"red","Shocked":"yellow","Frozen":"cyan"}
        t.color(color_map.get(c.status,"white"))
        t.write(c.status,align="center",font=("Arial",10,"bold"))

def update_all_visuals():
    update_health()
    update_status_icons()
    screen.update()

# ---------------------------
# Apply Status
# ---------------------------
def apply_status(c, opposing_team):
    if c.hp<=0: return
    if c.status=="Burned":
        c.hp-=5
        c.flash("orange")
        show_status_message(c,"Burned!","orange",c.message_count)
        c.message_count+=1
    elif c.status=="Bleeding":
        c.hp-=3
        c.flash("red")
        show_status_message(c,"Bleeding!","red",c.message_count)
        c.message_count+=1
    elif c.status=="Shocked":
        teammates = players if c.is_player else enemies
        for mate in teammates:
            if mate!=c and mate.hp>0:
                mate.hp-=3
                mate.flash("yellow")
                show_status_message(mate,"Shocked!","yellow",mate.message_count)
                mate.message_count+=1
    elif c.status=="Frozen":
        c.flash("cyan")
        show_status_message(c,"Frozen!","cyan",c.message_count)
        c.message_count+=1
    c.status_duration -=1
    if c.status_duration<=0: c.status=None
    clamp_hp(c)

# ---------------------------
# Attack Function
# ---------------------------
def attack_target(attacker, target, callback=None):
    update_all_visuals()
    ox, oy = attacker.x, attacker.y
    tx, ty = target.turtle.pos()
    total_hits = random.randint(1,2)
    def damage_hit(hit_num=1):
        base=random.randint(attacker.attack-2,attacker.attack+2)
        crit=random.random()<0.2
        dmg=base+2 if crit else base
        target.hp-=dmg
        clamp_hp(target)
        show_damage(target,dmg,crit,hit_num)
        shake_character(target,intensity=8 if crit else 4)
        particle_effect(target,count=5,color="orange")
        update_all_visuals()
        if hit_num<total_hits:
            screen.ontimer(lambda: damage_hit(hit_num+1),200)
        else:
            attacker.move_toward(ox,oy,callback=callback)
    attacker.move_toward(tx,ty,callback=lambda: damage_hit(1))

# ---------------------------
# Special Attack Animation
# ---------------------------
def special_attack_animation(attacker, target, callback=None):
    beam = turtle.Turtle()
    beam.hideturtle()
    beam.penup()
    beam.color("purple")
    beam.width(4)
    beam.goto(attacker.turtle.pos())
    beam.showturtle()
    steps = 15
    step = 0
    ox, oy = attacker.turtle.pos()
    tx, ty = target.turtle.pos()
    dx = (tx-ox)/steps
    dy = (ty-oy)/steps
    def animate():
        nonlocal step
        if step < steps:
            beam.goto(beam.xcor()+dx, beam.ycor()+dy)
            screen.update()
            step +=1
            screen.ontimer(animate,20)
        else:
            beam.hideturtle()
            beam.clear()
            if callback:
                callback()
    animate()

# ---------------------------
# Turn System
# ---------------------------
turn_queue=[]
def rebuild_turn_queue():
    global turn_queue
    turn_queue=[c for c in players+enemies if c.hp>0]

current_character=None
player_turn_pending=False
selected_enemy=None

def next_turn():
    global current_character, player_turn_pending
    # Reduce cooldowns for all characters
    for c in players + enemies:
        if c.special_cd > 0:
            c.special_cd -= 1
        for status in c.status_cd:
            if c.status_cd[status]>0:
                c.status_cd[status]-=1

    # Check game over
    if all(p.hp <= 0 for p in players):
        print("All players defeated! Game Over!")
        return
    if all(e.hp <= 0 for e in enemies):
        print("All enemies defeated! You win!")
        return

    if not turn_queue: rebuild_turn_queue()
    while turn_queue:
        current_character = turn_queue.pop(0)
        opposing = enemies if current_character.is_player else players
        apply_status(current_character, opposing)
        update_all_visuals()
        if current_character.hp <= 0: continue
        if current_character.status == "Frozen":
            print(f"{current_character.name} is frozen and skips turn!")
            screen.ontimer(next_turn, 500)
            return
        break
    else:
        screen.ontimer(next_turn, 500)
        return

    if current_character.is_player:
        player_turn_pending = True
        print(f"{current_character.name}'s turn - click enemy, press R for normal, S for special")
    else:
        tgt = random.choice([p for p in players if p.hp > 0])
        attack_target(current_character, tgt, callback=lambda: screen.ontimer(next_turn, 500))

# ---------------------------
# Enemy Selection
# ---------------------------
def select_enemy(x, y):
    global selected_enemy, player_turn_pending
    if not player_turn_pending:
        return
    for enemy in enemies:
        if enemy.hp <= 0: continue
        ex, ey = enemy.turtle.pos()
        if math.hypot(ex-x, ey-y) < 30:
            selected_enemy = enemy
            print(f"Selected {enemy.name}")
            break
screen.onclick(select_enemy)

# ---------------------------
# Player Attack Functions
# ---------------------------
def player_attack_regular():
    global player_turn_pending, selected_enemy
    if not player_turn_pending:
        return
    if selected_enemy is None or selected_enemy.hp <= 0:
        print("Select a valid enemy first!")
        return
    player_turn_pending = False
    attack_target(current_character, selected_enemy, callback=lambda: screen.ontimer(next_turn,500))
    selected_enemy = None

# ---------------------------
# Special Attack With Status Choice
# ---------------------------
def choose_status_for_special(character):
    print("Choose a status effect for the special (or 0 for None):")
    print("1: Burned, 2: Bleeding, 3: Shocked, 4: Frozen, 0: None")
    choice = input("Enter number: ")
    mapping = {"1":"Burned","2":"Bleeding","3":"Shocked","4":"Frozen","0":None}
    selected = mapping.get(choice,None)
    # Check cooldown
    if selected and character.status_cd.get(selected,0)>0:
        print(f"{selected} is on cooldown! Skipping status effect.")
        return None
    return selected

def player_attack_special():
    global player_turn_pending, selected_enemy
    if not player_turn_pending:
        return
    if selected_enemy is None or selected_enemy.hp <= 0:
        print("Select a valid enemy first!")
        return
    if current_character.special_cd > 0:
        print(f"Special on cooldown: {current_character.special_cd}")
        return
    player_turn_pending = False
    target_enemy = selected_enemy

    status_choice = choose_status_for_special(current_character)

    def after_special(target=target_enemy):
        target.hp -= current_character.attack + 5
        clamp_hp(target)
        if status_choice:
            target.status = status_choice
            target.status_duration = 2
            current_character.status_cd[status_choice] = 3
            print(f"{target.name} is now {status_choice}!")
        update_all_visuals()
        shake_character(target,intensity=10)
        particle_effect(target,count=10,color="purple")
        screen.ontimer(next_turn,500)

    special_attack_animation(current_character, target_enemy, callback=after_special)
    current_character.special_cd = 3
    selected_enemy = None

screen.onkey(player_attack_regular, "r")
screen.onkey(player_attack_special, "s")
screen.listen()

# ---------------------------
# Initialize
# ---------------------------
status_turtles={}
init_status_icons()
update_all_visuals()
rebuild_turn_queue()
screen.ontimer(next_turn,500)
screen.mainloop()
