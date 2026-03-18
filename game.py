# code for game

from gpiozero import Button
import os
import pygame

p1left = Button(23)
p1right = Button(24)
p1attack = Button(25)
p1block = Button(12)


p2left = Button(17)
p2right = Button(27)
p2attack = Button(22)
p2block = Button(5)

p1left.is_pressed = pygame.K_a
p1right.is_pressed = pygame.K_d
p1attack.is_pressed = pygame.K_w
p1block.is_pressed = pygame.K_e
p2left.is_pressed = pygame.K_LEFT 
p2right.is_pressed = pygame.K_RIGHT
p2attack.is_pressed = pygame.K_o
p2block.is_pressed = pygame.K_p

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()


# P1_LEFT = pygame.K_a
# P1_RIGHT = pygame.K_d
# P1_ATTACK = pygame.K_w
# P1_BLOCK = pygame.K_e
# P2_LEFT = pygame.K_LEFT
# P2_RIGHT = pygame.K_RIGHT
# P2_ATTACK = pygame.K_o
# P2_BLOCK = pygame.K_p

# gpioToPygameKey = {
#     p1left: P1_LEFT,
#     p1right: P1_RIGHT,
#     p1attack: P1_ATTACK,
#     p1block: P1_BLOCK,
#     p2left: P2_LEFT,
#     p2right: P2_RIGHT,
#     p2attack: P2_ATTACK,
#     p2block: P2_BLOCK
# }

