# -*- coding: utf-8 -*-
"""
 
 Q-Dino: The Quantum version of the Chrome Dino
 @jleonardoc

"""

import pygame, sys, os
from random import randint
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, execute, Aer

pygame.init()
main_window = pygame.display.set_mode((1000,400))
bg_color = pygame.Color(225,245,230)
shape_color = pygame.Color(20,16,152)
x_gate_color = pygame.Color(25,122,235)
h_gate_color = pygame.Color(25,182,115)
cnot_gate_color = pygame.Color(235,85,15)
text_color = pygame.Color(250,250,240)
label_color = pygame.Color(60,23,134)
plate_color = pygame.Color(45,94,46)
plate_color_inside = pygame.Color(85,194,46)
ocean_color = pygame.Color(25,112,245) 

dino_image = pygame.image.load('dino.png')
dino_image = pygame.transform.scale(dino_image, (80, 80))
cactus_image = pygame.image.load('cactus.png')
cactus_image = pygame.transform.scale(cactus_image, (200, 80))
cactus_crop = [(0, 0, 34, 80),
               (34, 0, 31, 80),
               (67, 0, 33, 80),
               (101, 0, 31, 80),
               (132, 0, 78, 80)]

main_font = pygame.font.Font(os.path.join("pixeboy-font", 'Pixeboy-z8XGD.ttf'), 30)
obstacles = [None, None, None, None, None, None, None, None, None, None,
             None, None, None, None, None, None, None, None, None, None,
             None, None, None, None, None, None, None, None, None, None,
             None, None, None, None, None, None, None, None, None, None,
             None, None, None, None, None, randint(0,len(cactus_crop)-1), 
             None, None, None, randint(0,len(cactus_crop)-1), None, None,
             None, None, None, None, None, randint(0,len(cactus_crop)-1),
             None, None, None, None, randint(0,len(cactus_crop)-1), -1]

levels = [
    ['x', 'cnot', 'cnoti', 'h','x','cnot'],
    ['x'],
    ['x'],
    ['x', 'x'],
    ['x', 'x'],
    ['h'],
    ['x', 'h']]

step = 0
level = 0
gates = levels[level]
applied_gates = [[], [], []]
active = 0
score = 0
high = 0
time = 80
stamp = 0
living = True
obstacle_separation = 70
h_velocity = 0.01

dino_x, dino_y = 10, 320
cactus_x, cactus_y = 10, 315
state = 'IDLE'

pos = 0
spaces = 0
jump = [[(4 * x - 0.05 * x * x) for x in range(36)],
        [(2.1 * x - 0.013 * x * x) for x in range(72)],
        [(1.5 * x - 0.00625 * x * x) for x in range(108)],
        [(1.05 * x - 0.003125 * x * x) for x in range(144)]]

def main(argv):
    pygame.display.set_caption('Q-Dino')
    while True:
        main_window.fill(bg_color)
        draw_circuit()
        draw_gates()
        draw_score()
        draw_time()
        draw_obstacles()
        draw_dino()
        event_listener()
        validate_cnot()
        if level == len(levels) and state == 'RUNNING':
            init_all()
        if int(step) == len(obstacles):
            init_all()
        pygame.display.update()
        pygame.time.wait(1)

def splash_screen():
    s = pygame.Surface((1000,750), pygame.SRCALPHA)
    s.fill((255,255,255,128))
    main_window.blit(s, (0,0))
    game_over = main_font.render("GAME OVER", 0, label_color)
    main_window.blit(game_over, (400, 300))
    pygame.display.update()
    pygame.time.wait(3000)

def event_listener():
    global active, stamp, level, gates, applied_gates, state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game()
        elif event.type == pygame.KEYDOWN and state in ('RUNNING', 'IDLE'):
            if stamp == 0:
                stamp = pygame.time.get_ticks()
                state = 'RUNNING'
            if event.key == pygame.K_DOWN:
                if active == 0:
                    if len(gates) > 0:
                        active = 1
                        applied_gates[0].append(gates.pop())
                elif active < len(applied_gates):
                    applied_gates[active].append(applied_gates[active-1].pop())
                    active += 1
                elif active == len(applied_gates):
                    active = 0
                    gates.append(applied_gates[2].pop())
            elif event.key == pygame.K_UP:
                if active == 0:
                    if len(gates) > 0:
                        active = len(applied_gates)
                        applied_gates[-1].append(gates.pop())
                elif active == 1:
                    active = 0
                    gates.append(applied_gates[0].pop())
                elif active <= len(applied_gates):
                    applied_gates[active-2].append(applied_gates[active-1].pop())
                    active -= 1
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                if active == 0 and gates[-1] == 'cnot':
                    gates[-1] = 'cnoti'
                elif active == 0 and gates[-1] == 'cnoti':
                    gates[-1] = 'cnot'
                elif len(applied_gates) > 0:
                    if len(applied_gates[active - 1]) > 0:
                        if applied_gates[active-1][-1] == 'cnot':
                            applied_gates[active-1][-1] = 'cnoti'
                        elif applied_gates[active-1][-1] == 'cnoti':
                            applied_gates[active-1][-1] = 'cnot'
            elif event.key == pygame.K_SPACE:
                if active != 0:
                    for i in range(len(applied_gates)):
                        if i != active - 1:
                            applied_gates[i].append('')
                    active = 0
                else:
                    gates.insert(0, gates.pop())
                if len(gates) == 0:
                    execute_dino()
                    if living:
                        level+=1
                    if level < len(levels):
                        gates = levels[level]
                    applied_gates = [[], [], []]
                    stamp = 0

def draw_score():
    global score, high
    score_lbl = main_font.render("HI   "
                                 + str(high).zfill(5) + "    " 
                                 + str(score).zfill(5), 0, label_color)
    main_window.blit(score_lbl, (780, 30))   

def draw_time():
    global stamp, time, gates
    if stamp > 0:
        seconds = time - int((pygame.time.get_ticks() - stamp)/1000)
        if seconds <= 0:
            execute_dino()
            gates = []
            stamp = 0
        minutes = 0
        if seconds >= 60:
            minutes = int(seconds / 60)
            seconds = seconds % 60
        time_lbl = main_font.render("TIME   " 
                                    + str(minutes).zfill(2) + ":" 
                                    + str(seconds).zfill(2), 0, label_color)
        main_window.blit(time_lbl, (500, 30))   

def draw_gates():
    x, y = 10, 10
    for gate in gates:
        if(gate == 'x'):
            draw_x_gate(x,y)
        elif(gate == 'h'):
            draw_h_gate(x,y)
        elif(gate == 'cnot'):
            draw_cnot_gate(x,y)
        elif(gate == 'cnoti'):
            draw_cnot_gate(x,y,True)
        x += 40

def draw_x_gate(x,y):
    pygame.draw.rect(main_window, x_gate_color, (x, y, 30,30), border_radius=5)
    pygame.draw.line(main_window, text_color, (x+7, y+7), (x+21, y+21), 4)
    pygame.draw.line(main_window, text_color, (x+7, y+21), (x+21, y+7), 4)
    
def draw_h_gate(x,y):
    pygame.draw.rect(main_window, h_gate_color, (x, y, 30,30), border_radius=5)
    pygame.draw.line(main_window, text_color, (x+9, y+7), (x+9, y+21), 4)
    pygame.draw.line(main_window, text_color, (x+19, y+21), (x+19, y+7), 4)
    pygame.draw.line(main_window, text_color, (x+9, y+14), (x+19, y+14), 4)
    
def draw_cnot_gate(x,y,rotated = False):
    up,down, val = 0, 50, 0
    if rotated:
        up,down, val = 50, 0, 10
    pygame.draw.circle(main_window, cnot_gate_color, (x + 15, y + up + 15 - val), 16)
    pygame.draw.circle(main_window, cnot_gate_color, (x + 15, y + down + 15 - val), 6)
    pygame.draw.line(main_window, cnot_gate_color, (x + 14, y + 15 - val),
                     (x + 14, y + 60 - val), 4)
    pygame.draw.line(main_window, text_color, (x+14, y+5+up-val), (x+14, y+24+up-val), 4)
    pygame.draw.line(main_window, text_color, (x+5, y+14+up-val), (x+24, y+14+up-val), 4)
        
def draw_circuit():
    ypos = [150, 200, 250]
    for i in range(len(ypos)):
        pygame.draw.line(main_window, shape_color, (50, ypos[i]), (900, ypos[i]), 3)
        label = main_font.render("q" + str(i), 0, label_color)
        main_window.blit(label, (10, ypos[i] - 10))
    for i in range(len(ypos)):
        x = 60
        for gate in applied_gates[i]:
            if(gate == 'x'):
                draw_x_gate(x,ypos[i] - 15)
            elif(gate == 'h'):
                draw_h_gate(x,ypos[i] - 15)
            elif(gate == 'cnot'):
                draw_cnot_gate(x,ypos[i] - 15)
            elif(gate == 'cnoti'):
                draw_cnot_gate(x,ypos[i] - 5 - 50, True)    
            x += 40

def draw_dino():
    global state, step, pos, score, high
    if state == 'IDLE':
        main_window.blit(dino_image, (dino_x, dino_y))
    elif state == 'RUNNING' or state == 'DUCKING':
        prev_step = step
        step += h_velocity
        if int(prev_step) != int(step):
            score += 1
            high = max(high, score)
        main_window.blit(dino_image, (dino_x, dino_y))
    elif state == 'JUMPING':
        step += h_velocity * (spaces + 1)
        main_window.blit(dino_image, (dino_x,dino_y - jump[spaces][pos]))
        pos += spaces + 1
        if pos >= len(jump[spaces]):
            state = 'FALLING'
            pos = len(jump[spaces]) - 1
    elif state == 'FALLING':
        step += h_velocity * (spaces + 1)
        main_window.blit(dino_image, (dino_x,dino_y - jump[spaces][pos]))
        pos -= spaces + 1
        if pos <= 0:
            state = 'RUNNING'
            pos = 0
            
def draw_obstacles():
    for obs in range(int(step) - 1, len(obstacles)):
        x = cactus_x + ((obs - step) * obstacle_separation) - 15
        y = cactus_y + 60
        if x > -obstacle_separation * 2:
            if obstacles[obs] == -1 and int(step) > 0:
                pygame.draw.polygon(main_window, ocean_color,
                                    [[x,y],[x+20,y+25],[x+1288, y+25],[x+1268,y]])
            else:
                pygame.draw.polygon(main_window, plate_color,
                                    [[x,y],[x+20,y+25],[x+88, y+25],[x+68,y]])
                pygame.draw.polygon(main_window, plate_color_inside,
                                    [[x+12,y+5],[x+25,y+20],[x+78, y+20],[x+63,y+5]])
                if obstacles[obs] != None and obstacles[obs] != -1:
                    xpos = cactus_x + ((obs - step) * obstacle_separation);
                    ypos = cactus_y
                    main_window.blit(cactus_image, 
                                    (xpos,
                                     ypos), 
                                    cactus_crop[obstacles[obs]])
                    validate_collision(xpos, ypos, cactus_crop[obstacles[obs]])

def validate_collision(xpos, ypos, obs):
    if dino_x + 65 >= xpos and dino_x + 65 <= xpos + obs[2]:
        if state == "RUNNING" or state == "DUCKING":
            init_all()
    if dino_x >= xpos and dino_x <= xpos + obs[2]:
        if state == "RUNNING" or state == "DUCKING":
            init_all()
            
def validate_cnot():
    global active
    if len(applied_gates[-1]) > 0:
        if applied_gates[-1][-1] == 'cnot':
            applied_gates[-1][-1] = 'cnoti'
    if len(applied_gates[0]) > 0:
        if applied_gates[0][-1] == 'cnoti':
            applied_gates[0][-1] = 'cnot'
            
def execute_dino():
    qr = QuantumRegister(len(applied_gates), 'q')
    cr = ClassicalRegister(len(applied_gates), 'c')
    circuit = QuantumCircuit(qr, cr)
    
    for gate in range(len(applied_gates[0])):
        for line in range(len(applied_gates)):
            if applied_gates[line][gate] == 'x':
                circuit.x(qr[line])
            elif applied_gates[line][gate] == 'h':
                circuit.h(qr[line])
            elif(applied_gates[line][gate] == 'cnot'):
                circuit.cnot(qr[line + 1], qr[line])
            elif(applied_gates[line][gate] == 'cnoti'):
                circuit.cnot(qr[line - 1], qr[line])
                
    for i in range(len(applied_gates)):
        circuit.measure(qr[i], cr[i])
    
    backend = Aer.get_backend('qasm_simulator')
    job_sim = execute(circuit, backend, shots=1024)
    sim_result = job_sim.result()
    measurement_result = sim_result.get_counts(circuit)
    print(measurement_result)
    play_dino(measurement_result)
    
def play_dino(measurement_result):
    global step, score, high, state, pending_steps, pos, spaces
    action = max(measurement_result, key=measurement_result.get)
    # The first classical bit indicates if the Q-Dino will jump or duck
    # 0 = Jump, 1 = Duck
    # The second and third bit indicates the number of spaces Q-Dino will move
    # 00 = Run 1 space, 01 = Jump 2 spaces, 10 = Jump 3 spaces, 11 = Jump 4 spaces 
    if(action[0] == '0'):
        state = "JUMPING"
    else:
        state = "DUCKING"
    
    spaces = int(action[1:], 2)
    score += 10 * (spaces + 1)
    high = max(high, score)
    pos = 0
    
    print(state + " kind " + str(spaces + 1))

def init_all():
    global step, levels, level, gates, applied_gates, active, score, time, \
    stamp, living, obstacle_separation, h_velocity, state, pos, spaces, \
    obstacles
    levels = [
        ['x'],
        ['x'],
        ['x', 'x'],
        ['x', 'x'],
        ['h'],
        ['x', 'h']]
    
    obstacles = [None, None, None, None, None, randint(0,len(cactus_crop)-1), 
             None, None, None, randint(0,len(cactus_crop)-1), None, None,
             None, None, None, None, None, randint(0,len(cactus_crop)-1),
             None, None, None, None, randint(0,len(cactus_crop)-1), -1]

    step = 0
    level = 0
    gates = levels[level]
    applied_gates = [[], [], []]
    active = 0
    score = 0
    time = 80
    stamp = 0
    living = True
    obstacle_separation = 70
    h_velocity = 0.01
    state = 'IDLE'
    pos = 0
    spaces = 0
    splash_screen()

def exit_game():
    pygame.quit()
    sys.exit()
        
if __name__ == "__main__":
    main(sys.argv)