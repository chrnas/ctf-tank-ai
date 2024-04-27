#pip install pymunk==5.7.0
#pip install pygame==2.0.1
#pip install playsound


import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
from pymunk import Vec2d
import argparse
import time
import copy
#----- Initialisation -----#
#-- Initialise the display
pygame.init()
pygame.display.set_mode()

#initialize music
pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
pygame.mixer.init()

#-- Initialise the clock
clock = pygame.time.Clock()
clock1 = pygame.time.Clock()
pygame.time.set_timer(pygame.USEREVENT, 1000)#thousand milliseconds 
counter = 300

#-- Initialise the physics engine
space = pymunk.Space()
space.gravity = (0.0,  0.0)
space.damping = 0.1 # Adds friction to the ground for all objects

#argparse
parser = argparse.ArgumentParser()
parser.add_argument("-s","--singleplayer", help="singleplayer",action="store_true")
parser.add_argument("-m","--multiplayer", help="multiplayer", action="store_true")
parser.add_argument("-c","--countdown", help="countdown",action="store_true")
parser.add_argument("-f","--highestscore", help="highestscore",action="store_true")
parser.add_argument("-r","--roundlimit", help="round_limit",action="store_true")
args = parser.parse_args()
number_players = 0

if args.singleplayer:
    number_players = 1
if args.multiplayer:
    number_players = 2
if args.roundlimit:
    text = '0'.rjust(1)
if args.countdown:
    text = '300'.rjust(3)

#-- Import from the ctf framework
import ai
import images
import gameobjects
import maps

#-- Constants
FRAMERATE = 50

#-- Variables
#   Define the current level
current_map         = maps.map0

#   List of all game objects
game_objects_list   = []
tanks_list          = []
ai_list             = []
new_ai_list         = []

# Timer
start_timer = 0

#-- Resize the screen to the size of the current level
screen = pygame.display.set_mode(current_map.rect().size)

#-- Generate the background
background = pygame.Surface(screen.get_size())

#Font for score_Board
font = pygame.font.SysFont('Consolas', 30)
font2 = pygame.font.SysFont('Consolas', 15)

collision_types = {
    "bullet": 1,
    "tank": 2,
    "woodenbox": 3,
    "stonebrick": 4,
    "ironblock": 5,
    "wall": 6
}


def create_grass():
    """Copy the grass tile all over the level area"""
    for x in range(0, current_map.width):
        for y in range(0, current_map.height):
            #The call to the function "blit" will copy the image
            # contained in "images.grass" into the "background"
            # image at the coordinates given as the second argument
            background.blit(images.grass, (x*images.TILE_SIZE, y*images.TILE_SIZE))


def create_boxes():
    """create boxes of different types, depending on the map pattern"""
    for x in range(0, current_map.width):
        for y in range(0, current_map.height):
            #Get the type of boxes
            box_type = current_map.boxAt(x, y)
            # If the box type is not 0 (aka grass tile), create a box
            if(box_type != 0):
                #Create a "Box" using the box_type, aswell as the x,y coordinates,
                # and the pymunk space
                box = gameobjects.get_box_with_type(x, y, box_type, space)
                game_objects_list.append(box)


def create_tanks():
    """Create all the tanks both controlled by ai and player"""
    for i in range(0, len(current_map.start_positions)):
        # Get the starting position of the tank "i"
        pos = current_map.start_positions[i]
        # Create the tank, images.tanks contains the image representing the tank
        tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[i], space)
        # Add the tank to the list of tanks
        tanks_list.append(tank)


def create_ai():
    """Creates the ai"""
    for i in range(number_players, len(tanks_list)):
        ais = ai.Ai(tanks_list[i], game_objects_list, tanks_list, space, current_map)
        ai_list.append(ais)

#Create the flag
flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
game_objects_list.append(flag)


def init_walls(space): 
    """Initializes the four outer walls of the board"""
    for x in range(-1, current_map.width + 1):
        for y in range(-1, current_map.height + 1):
            if current_map.width <= x or x < 0 or current_map.height <= y or y < 0: 
                box = gameobjects.get_box_with_type(x, y, 1, space)
                game_objects_list.append(box)


#Create bases
def create_bases():
    """Create starting positions for the tanks"""
    for i in range(0, len(current_map.start_positions)):
        pos = current_map.start_positions[i]
        base = gameobjects.GameVisibleObject(pos[0], pos[1], images.bases[i])
        game_objects_list.append(base)

#Build game world
create_bases()
create_grass()
init_walls(space)
create_tanks()
create_boxes()
create_ai()

#----- Main Loop -----#

#-- Control whether the game run
running = True

#Create variables
skip_update = 0
score_player1 = 0
score_player2 = 0
round_count_nr = 0
timer = 10000000

#Background  music
sound_main_music = pygame.mixer.Sound("data//main_music.wav")
sound_main_music.set_volume(0.05)
sound_main_music.play()

#Running of the game
while running:
    #-- Handle the events
    for event in pygame.event.get():
        # Check if we receive a QUIT event (for instance, if the user press the
        # close button of the window or if the user presses the escape key.


        def shoot_times(tank):
            bullet = tank.shoot(space)
                
            if type(bullet) != bool:
                game_objects_list.append(bullet)
                sound_tank_fire = pygame.mixer.Sound("data//tank-fire.wav")
                sound_tank_fire.set_volume(0.2)
                sound_tank_fire.play()
                
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False
        
        #code for singleplayer movement
        if args.singleplayer or args.multiplayer:
            if event.type == KEYDOWN and event.key == K_UP:
                tanks_list[0].accelerate()
            if event.type == KEYUP and event.key == K_UP:
                tanks_list[0].stop_moving()
            if event.type == KEYDOWN and event.key == K_DOWN:
                tanks_list[0].decelerate()
            if event.type == KEYUP and event.key == K_DOWN:
                tanks_list[0].stop_moving()
            if event.type == KEYDOWN and event.key == K_LEFT:
                tanks_list[0].turn_left()
            if event.type == KEYUP and event.key == K_LEFT:
                tanks_list[0].stop_turning()
            if event.type == KEYDOWN and event.key == K_RIGHT:
                tanks_list[0].turn_right()
            if event.type == KEYUP and event.key == K_RIGHT:
                tanks_list[0].stop_turning()
            if event.type == KEYUP and event.key == K_SPACE:
                shoot_times(tanks_list[0])                                 
    

        def score_count():
            for i in range(len(tanks_list)):
                print("Spelare", i+1, ": ", tanks_list[i].score)

            
        while timer < counter:
            timer += 0.0005
            screen.fill((200, 200, 200))
            selection_text =  'score player 1: ' + str(tanks_list[0].score)
            selection_text2 = 'score player 2: ' + str(tanks_list[1].score)
            screen.blit(font2.render(selection_text, True, (0, 0, 0)), (20, 30 + 30))
            screen.blit(font2.render(selection_text2, True, (0, 0, 0)), (20, 30 + 60))
            selection_text5 = 'Round: ' + str(round_count_nr)
            if len(tanks_list) > 2:
                selection_text3 = 'score player 3: ' + str(tanks_list[2].score)
                selection_text4 = 'score player 4: ' + str(tanks_list[3].score)
                screen.blit(font2.render(selection_text3, True, (0, 0, 0)), (20, 30 + 90))
                screen.blit(font2.render(selection_text4, True, (0, 0, 0)), (20, 30 + 120))
            if len(tanks_list) > 4:
                selection_text6 = 'score player 5: ' + str(tanks_list[4].score)
                selection_text7 = 'score player 6: ' + str(tanks_list[5].score)
                screen.blit(font2.render(selection_text6, True, (0, 0, 0)), (20, 30 + 150))
                screen.blit(font2.render(selection_text7, True, (0, 0, 0)), (20, 30 + 180))


            screen.blit(font.render(selection_text5, True, (0, 0, 0)), (70, 20))
            pygame.display.flip()     

        if event.type == pygame.USEREVENT: 
            counter -= 1 #reduces the time
            
        #Code for multiplayer movement
        if args.multiplayer:            
            if event.type == KEYDOWN and event.key == K_w:
                tanks_list[1].accelerate()
            if event.type == KEYUP and event.key == K_w:
                tanks_list[1].stop_moving()
            if event.type == KEYDOWN and event.key == K_s:
                tanks_list[1].decelerate()
            if event.type == KEYUP and event.key == K_s:
                tanks_list[1].stop_moving()       
            if event.type == KEYDOWN and event.key == K_a:
                tanks_list[1].turn_left()
            if event.type == KEYUP and event.key == K_a:
                tanks_list[1].stop_turning()
            if event.type == KEYDOWN and event.key == K_d:
                tanks_list[1].turn_right()
            if event.type == KEYUP and event.key == K_d:
                tanks_list[1].stop_turning()       
            if event.type == KEYUP and event.key == K_r:
                game_objects_list.append(tanks_list[1].shoot(space))


    def tank_bullet(arbiter, space, data):
        """Code for what happens if a bullet hits a tank"""
        bullet_shape = arbiter.shapes[0]
        space.remove(bullet_shape, bullet_shape.body)
        arbiter.shapes[1].parent.hitpoints = arbiter.shapes[1].parent.hitpoints - 1
        try:
            game_objects_list.remove(bullet_shape.parent)
        except ValueError:
            pass
        if arbiter.shapes[1].parent.hitpoints <= 0:
            arbiter.shapes[1].parent.remove_flag(flag)
            arbiter.shapes[1].parent.body.position = arbiter.shapes[1].parent.start_position
            arbiter.shapes[1].parent.body.angle = arbiter.shapes[1].parent.start_orientation
            flag.is_on_tank = False
            for ais in ai_list:
                ais.update_grid_pos()
            arbiter.shapes[1].parent.shape.collision_type = 4 #change to 4
            arbiter.shapes[1].parent.death_timer = 0 #resets death_timer back to zero
            arbiter.shapes[1].parent.hitpoints = 3
            sound_tank_explode = pygame.mixer.Sound("data//tank-explosion.wav")
            sound_tank_explode.set_volume(1)
            sound_tank_explode.play()
        return False

    def resapwn_protection():
        for i in range(0, len(current_map.start_positions)): #every tank in the game
            if tanks_list[i].death_timer > 200:
                tanks_list[i].shape.collision_type = 2
                tanks_list[i].death_timer = 0
    
    resapwn_protection()
       
    def box_bullet(arbiter,space,data):
        """Code for what happens if a bullet hits a box"""
        bullet_shape = arbiter.shapes[0]
        box_shape = arbiter.shapes[1]
        space.remove(bullet_shape, bullet_shape.body)
        arbiter.shapes[1].parent.hitpoints = arbiter.shapes[1].parent.hitpoints - 1
        if bullet_shape.parent in game_objects_list:
            game_objects_list.remove(bullet_shape.parent)
        if arbiter.shapes[1].parent.hitpoints <= 0:
            game_objects_list.remove(box_shape.parent)         
            space.remove(box_shape, box_shape.body)
            sound_tank_box = pygame.mixer.Sound("data//crate-break.wav")
            sound_tank_box.set_volume(1)
            sound_tank_box.play()
        return False


    def stone_bullet(arbiter,space,data):
        """Code for what happens if a bullet hits a stone"""
        bullet_shape = arbiter.shapes[0]
        space.remove(bullet_shape, bullet_shape.body)
        game_objects_list.remove(bullet_shape.parent)
        sound_tank_box = pygame.mixer.Sound("data//concrete_wall.wav")
        sound_tank_box.set_volume(0.06)
        sound_tank_box.play()
        return False


    def metall_bullet(arbiter,space,data):
        """Collisionhandler for when a bullet hits a metal box"""
        bullet_shape = arbiter.shapes[0]
        space.remove(bullet_shape, bullet_shape.body)
        game_objects_list.remove(bullet_shape.parent)
        sound_tank_box = pygame.mixer.Sound("data//metal_wall.wav")
        sound_tank_box.set_volume(0.5)
        sound_tank_box.play()
        return False
    

    collision_woodbox = space.add_collision_handler(collision_types["bullet"], collision_types["woodenbox"]) #Checks if bullet hits woodenbox 
    collision_woodbox.pre_solve = box_bullet

    collision_tank = space.add_collision_handler(collision_types["bullet"], collision_types["tank"]) #Checks if bullet hits tank
    collision_tank.pre_solve = tank_bullet

    collision_stoneblock = space.add_collision_handler(collision_types["bullet"], collision_types["stonebrick"]) #Checks if the bullet hits stonebox
    collision_stoneblock.pre_solve = stone_bullet

    collison_ironblock = space.add_collision_handler(collision_types["bullet"], collision_types["ironblock"]) #checks if bullet hits metalbox
    collison_ironblock.pre_solve = metall_bullet

    #-- Update physics
    if skip_update == 0:
        # Loop over all the game objects and update their speed in function of their
        # acceleration.
        for obj in game_objects_list:
            try:
                obj.update()
                skip_update = 2
            except AttributeError:
                pass
    else:
        skip_update -= 1

    #   Check collisions and update the objects position
    space.step(1 / FRAMERATE)

    #   Update object that depends on an other object position (for instance a flag)
    for obj in game_objects_list:
        try:
            obj.post_update()
        except AttributeError:
            pass

    # Display the background on the screen
    screen.blit(background, (0, 0))

    #Update the display of the game objects on the screen
    for obj in game_objects_list:
        try:
            obj.update()
            obj.update_screen(screen)
        except AttributeError:
            pass
            
       
    for tank in tanks_list:
        tank.try_grab_flag(flag)
        tank.post_update()
        tank.update()
        tank.update_screen(screen)
        tank.try_grab_flag(flag)
        if tank.has_won():
            timer = counter - 3
            tank.score += 1
            round_count_nr += 1
            print("round: ", round_count_nr)
            tank.max_speed  = tank.NORMAL_MAX_SPEED
            tank.remove_flag(flag)
            flag.move_flag_back(current_map.flag_position[0], current_map.flag_position[1])
            score_count()
            sound_stage_win = pygame.mixer.Sound("data//stage_win_sound.wav")
            sound_stage_win.set_volume(5)
            sound_stage_win.play()

    for ai in ai_list:
        ai.decide()
    
    if args.countdown:
        #The game continues until the timer is 0
        if counter == 0:
            highest_score = [0, 0]
            for i in range (len(tanks_list)):
                if tanks_list[i].score > highest_score[0]:
                    highest_score = [tanks_list[i].score, i]
            print("Vinnaren är: Tank ", highest_score[1] + 1)
            running = False
        if event.type == USEREVENT:
            text = str(counter).rjust(3)
        screen.blit(font.render(text, True, (0, 0, 0)), (2, 2))
    
    if args.highestscore:
        #Win condition, quits if a tank has captured the flag 5 times
        for i in range(len(tanks_list)):
            if tanks_list[i].score >= 5:
                print('Spelare', i, 'har vunnit.')
                running = False
    
    if args.roundlimit:
        #Win condition, quits if 10 rounds have been reached
        if event.type == USEREVENT:
            text = str(round_count_nr).rjust(1)
        if round_count_nr > 9:
            running = False
        screen.blit(font.render(text, True, (0, 0, 0)), (5, 2))
    
    #-- Update Display
    #   Redisplay the entire screen (see double buffer technique)
    pygame.display.flip()
    #   Control the game framerate
    clock.tick(FRAMERATE)
    clock1.tick(60)

