# code for game

from gpiozero import Button
import os
import pygame


SCREEN_W   = 1280
SCREEN_H   = 720
FPS        = 60
SCALE      = 2.5
FRAME_SIZE = 128
MOVE_SPEED = 5
GROUND_Y   = SCREEN_H - 90
MAX_HP     = 100


# p1left = Button(23)
# p1right = Button(24)
# p1attack = Button(25)
# p1block = Button(12)


# p2left = Button(17)
# p2right = Button(27)
# p2attack = Button(22)
# p2block = Button(5)

# p1left.is_pressed = pygame.K_a
# p1right.is_pressed = pygame.K_d
# p1attack.is_pressed = pygame.K_w
# p1block.is_pressed = pygame.K_e
# p2left.is_pressed = pygame.K_LEFT 
# p2right.is_pressed = pygame.K_RIGHT
# p2attack.is_pressed = pygame.K_o
# p2block.is_pressed = pygame.K_p


# P1_LEFT = pygame.K_a
# P1_RIGHT = pygame.K_d
# P1_ATTACK = pygame.K_w
# P1_BLOCK = pygame.K_e
# P2_LEFT = pygame.K_LEFT
# P2_RIGHT = pygame.K_RIGHT
# P2_ATTACK = pygame.K_o
# P2_BLOCK = pygame.K_p

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

    # ── draw
 
    def draw(self, surface):
        frame = self.sheets[self.state].get(self.frame_index)
        if self.facing == -1:
            frame = pygame.transform.flip(frame, True, False)
        y = GROUND_Y - frame.get_height()
        surface.blit(frame, (int(self.x), y))
 
 
#hp
def draw_hp_bars(surface, f1, f2, font):
    bar_w = int(SCREEN_W * 0.3)   # 30% of screen width
    bar_h = int(SCREEN_H * 0.04)  # 4% of screen height
    margin = int(SCREEN_W * 0.03) # 3% of screen width
    y = int(SCREEN_H * 0.04)      # 4% from top

    # P1— left side
    pygame.draw.rect(surface, (80, 0, 0),    (margin, y, bar_w, bar_h), border_radius=6)
    pygame.draw.rect(surface, (200, 40, 40), (margin, y, int(bar_w * f1.hp / MAX_HP), bar_h), border_radius=6)
    pygame.draw.rect(surface, (255, 255, 255),(margin, y, bar_w, bar_h), 2, border_radius=6)
    surface.blit(font.render(f"P1  {f1.hp}", True, (255, 255, 255)), (margin + 8, y + 4))

    # P2 — right side
    x2   = SCREEN_W - margin - bar_w
    fill = int(bar_w * f2.hp / MAX_HP)
    pygame.draw.rect(surface, (80, 0, 0),    (x2, y, bar_w, bar_h), border_radius=6)
    pygame.draw.rect(surface, (200, 40, 40), (x2 + bar_w - fill, y, fill, bar_h), border_radius=6)
    pygame.draw.rect(surface, (255, 255, 255),(x2, y, bar_w, bar_h), 2, border_radius=6)
    lbl = font.render(f"{f2.hp}  P2", True, (255, 255, 255))
    surface.blit(lbl, (x2 + bar_w - lbl.get_width() - 8, y + 4))


# Pygame Setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

# Positions for players
p1Pos = pygame.Vector2(screen.get_width() / 4, screen.get_height() * 0.6)
p2Pos = pygame.Vector2(screen.get_width() / 4 * 3, screen.get_height() * 0.6)


# Load background image
try:
    bg1 = pygame.image.load("static/images/background.png").convert()
    bg1 = pygame.transform.scale(bg1, (1280, 720))
except Exception:
    bg1 = None  # fallback if no background image

# Load player 1 idle sprite sheet
idle_path_p1, idle_frames_p1, idle_scale_p1 = SPRITE_DEF["p1"]["idle"]
p1_idle_spritesheet = SpriteSheet(idle_path_p1, idle_frames_p1, idle_scale_p1 / 2)

# Load player 2 idle sprite sheet
idle_path_p2, idle_frames_p2, idle_scale_p2 = SPRITE_DEF["p2"]["idle"]
p2_idle_spritesheet = SpriteSheet(idle_path_p2, idle_frames_p2, idle_scale_p2 / 2)

# Frame indices for animations
frame_index_p1 = 0.0
frame_index_p2 = 0.0

animation_speed = 7  # frames per second

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill screen with purple as fallback background color
    screen.fill("purple")

    # Draw background if loaded
    if bg1:
        screen.blit(bg1, (0, 0))

    move_speed = 5  # pixels per frame


    keys = pygame.key.get_pressed()

    # Player 1 movement
    if keys[pygame.K_a]:
        p1Pos.x -= move_speed
    if keys[pygame.K_d]:
        p1Pos.x += move_speed

    # Player 2 movement
    if keys[pygame.K_LEFT]:
        p2Pos.x -= move_speed
    if keys[pygame.K_RIGHT]:
        p2Pos.x += move_speed

    # Optional: keep players inside screen bounds horizontally
    p1Pos.x = max(0, min(screen.get_width(), p1Pos.x))
    p2Pos.x = max(0, min(screen.get_width(), p2Pos.x))


    # Animate player 1 idle sprite
    frame_index_p1 += animation_speed * clock.get_time() / 1000.0  # advance frame based on time elapsed
    if frame_index_p1 >= len(p1_idle_spritesheet):
        frame_index_p1 = 0.0

    current_frame_p1 = p1_idle_spritesheet.get(frame_index_p1)
    rect_p1 = current_frame_p1.get_rect(center=(int(p1Pos.x), int(p1Pos.y)))
    screen.blit(current_frame_p1, rect_p1)

    # Animate player 2 idle sprite
    frame_index_p2 += animation_speed * clock.get_time() / 1000.0  # advance frame based on time elapsed
    if frame_index_p2 >= len(p2_idle_spritesheet):
        frame_index_p2 = 0.0

    current_frame_p2 = p2_idle_spritesheet.get(frame_index_p2)
    current_frame_p2 = pygame.transform.flip(current_frame_p2, True, False)
    rect_p2 = current_frame_p2.get_rect(center=(int(p2Pos.x), int(p2Pos.y)))
    screen.blit(current_frame_p2, rect_p2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

