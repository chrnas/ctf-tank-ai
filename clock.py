import pygame
import math
pygame.init()
screen = pygame.display.set_mode((512, 512))
clock = pygame.time.Clock()

text = 'WELCOME'.rjust(5)
font = pygame.font.SysFont('Consolas', 80)
selection_text = 'for single player press 1'
selection_text2 = 'for hotseat multiplayer press 2'
font2 = pygame.font.SysFont('Consolas', 30)

run = True
while run:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: 
            run = False

    screen.fill((0, 255, 255))
    screen.blit(font.render(text, True, (50, 200, 20)), (85, 100))#text, something, color, starting position
    screen.blit(font2.render(selection_text, True, (50, 200, 20)), (20, 200))
    screen.blit(font2.render(selection_text2, True, (50, 200, 20)), (20, 300))
    pygame.display.flip()
    
    clock.tick(50)