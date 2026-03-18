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

SPRITE_DEF = {
    "p1": {
        "idle":    ("static/images/Idle1.png",     6,  8),
        "walk":    ("static/images/Walk1.png",     8, 12),
        "attack1": ("static/images/Attack1.1.png", 6, 14),  # basic attack
        "attack2": ("static/images/Attack1.2.png", 6, 10),  # back + attack (heavy)
        "special": ("static/images/Special1.png",  8, 14),  # forward + attack
        "hurt":    ("static/images/Hurt1.png",     4, 12),
        "dead":    ("static/images/Dead1.png",     6,  8),
    },
    "p2": {
        "idle":    ("static/images/Idle2.png",     7,  8),
        "walk":    ("static/images/Walk2.png",     8, 12),
        "attack1": ("static/images/Attack2.1.png", 6, 14),
        "attack2": ("static/images/Attack2.3.png", 6, 10),
        "special": ("static/images/Special1.png",  8, 14),  # same as p1
        "hurt":    ("static/images/Hurt2.png",     4, 12),
        "dead":    ("static/images/Dead2.png",     6,  8),
    },
}
# Which animation frames are "active" (can deal damage)
ACTIVE_FRAMES = {
    "attack1": (2, 4),
    "attack2": (2, 5),
    "special": (3, 6),
}
 
# How long each attack and hurt animation plays before going back to idle
ATTACK_DURATION = {
    "attack1": 0.43,
    "attack2": 0.60,
    "special": 0.57,
    "hurt":    0.33,
}
class SpriteSheet:
    def __init__(self, path, frame_count, scale):
        sheet = pygame.image.load(path).convert_alpha()
        size  = int(FRAME_SIZE * scale)
        self.frames = [
            pygame.transform.scale(
                sheet.subsurface(pygame.Rect(i * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE)),
                (size, size)
            )
            for i in range(frame_count)
        ]
 
    def get(self, index):
        return self.frames[int(index) % len(self.frames)]
 
    def __len__(self):
        return len(self.frames)