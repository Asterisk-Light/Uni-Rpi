# code for game

try:
    from gpiozero import Button
except ImportError:
    pass
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
        "attack1": ("static/images/Attack1.1.png", 5, 14),  # basic attack
        "attack2": ("static/images/Attack1.2.png", 3, 10),  # back + attack (heavy)
        "hurt":    ("static/images/Hurt1.png",     3, 12),
        "dead":    ("static/images/Dead1.png",     4,  8),
    },
    "p2": {
        "idle":    ("static/images/Idle2.png",     7,  8),
        "walk":    ("static/images/Walk2.png",     8, 12),
        "attack1": ("static/images/Attack2.1.png", 4, 14),
        "attack2": ("static/images/Attack2.3.png", 4, 10), # same as p1
        "hurt":    ("static/images/Hurt2.png",     3, 12),
        "dead":    ("static/images/Dead2.png",     4,  8),
    },
}
# Which animation frames are "active" (can deal damage)
ACTIVE_FRAMES = {
    "attack1": (2, 4),
    "attack2": (2, 5),
    "special": (3, 6),
}
 
ATTACK_DAMAGE = {
    "attack1": 10,
    "attack2": 22,
    "special": 30,
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

COMBO_WINDOW = 0.4
 
class Fighter:
    def __init__(self, player_key, start_pos, facing):
        self.player_key  = player_key
        self.pos         = pygame.Vector2(start_pos)
        self.facing      = facing
        self.state       = "idle"
        self.frame_index = 0.0
        self.hp          = MAX_HP
        self.dead        = False
 
        self.attacking    = False
        self.attack_type  = None
        self.attack_timer = 0.0
        self.hit_landed   = False
 
        self.hurting    = False
        self.hurt_timer = 0.0
 
        self.back_pressed_at = -999.0
        self.fwd_pressed_at  = -999.0
 
        self.sheets   = {}
        self.anim_fps = {}
        for anim, (path, count, fps) in SPRITE_DEF[player_key].items():
            self.sheets[anim]   = SpriteSheet(path, count, SCALE)
            self.anim_fps[anim] = fps
 
    @property
    def scaled_size(self):
        return int(FRAME_SIZE * SCALE)
 
    @property
    def rect(self):
        w = int(self.scaled_size * 0.8)
        h = self.scaled_size
        x = int(self.pos.x) - w // 2
        y = GROUND_Y - h
        return pygame.Rect(x, y, w, h)
 
    def set_state(self, new_state):
        if self.state != new_state:
            self.state       = new_state
            self.frame_index = 0.0
 
    def _advance_frame(self, dt):
        self.frame_index += self.anim_fps[self.state] * dt
        total = len(self.sheets[self.state])
        if self.frame_index >= total:
            self.frame_index = 0.0
 
    def take_hit(self, damage):
        if self.dead or self.hurting:
            return
        self.hp = max(0, self.hp - damage)
        if self.hp == 0:
            self.dead = True
            self.set_state("dead")
        else:
            self.hurting     = True
            self.hurt_timer  = ATTACK_DURATION["hurt"]
            self.attacking   = False
            self.attack_type = None
            self.set_state("hurt")
 
    def try_attack(self, now, back_held, fwd_held):
        if self.attacking or self.hurting or self.dead:
            return
        if fwd_held or (now - self.fwd_pressed_at) < COMBO_WINDOW:
            atype = "special" if "special" in self.sheets else "attack1"
        elif back_held or (now - self.back_pressed_at) < COMBO_WINDOW:
            atype = "attack2"
        else:
            atype = "attack1"
        self.attacking    = True
        self.attack_type  = atype
        self.attack_timer = ATTACK_DURATION[atype]
        self.hit_landed   = False
        self.set_state(atype)
 
    def update(self, dt, left_held, right_held, now, opponent):
        if self.dead:
            self._advance_frame(dt)
            total = len(self.sheets["dead"])
            if self.frame_index >= total - 1:
                self.frame_index = float(total - 1)
            return
 
        if self.hurting:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.hurting = False
                self.set_state("idle")
            self._advance_frame(dt)
            return
 
        if self.attacking:
            self.attack_timer -= dt
            cur = int(self.frame_index)
            a_start, a_end = ACTIVE_FRAMES.get(self.attack_type, (2, 4))
            if not self.hit_landed and a_start <= cur <= a_end:
                reach = self.rect.inflate(int(self.scaled_size * 0.5), 0)
                if self.facing == 1:
                    reach.x = self.rect.right - reach.width // 4
                else:
                    reach.x = self.rect.left - reach.width * 3 // 4
                if reach.colliderect(opponent.rect):
                    opponent.take_hit(ATTACK_DAMAGE[self.attack_type])
                    self.hit_landed = True
            if self.attack_timer <= 0:
                self.attacking   = False
                self.attack_type = None
                self.set_state("idle")
            self._advance_frame(dt)
            return
 
        if self.facing == 1:
            back_dir = left_held
            fwd_dir  = right_held
        else:
            back_dir = right_held
            fwd_dir  = left_held
 
        if back_dir:
            self.back_pressed_at = now
        if fwd_dir:
            self.fwd_pressed_at = now
 
        moving = False
        if left_held:
            self.pos.x -= MOVE_SPEED
            self.facing  = -1
            moving       = True
        if right_held:
            self.pos.x += MOVE_SPEED
            self.facing  = 1
            moving       = True
 
        self.pos.x = max(0, min(SCREEN_W, self.pos.x))
        self.set_state("walk" if moving else "idle")
        self._advance_frame(dt)
 
    def draw(self, surface):
        frame = self.sheets[self.state].get(self.frame_index)
        if self.facing == -1:
            frame = pygame.transform.flip(frame, True, False)
        rect = frame.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        surface.blit(frame, rect)

def draw_win_screen(surface, text, font):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    rendered = font.render(text, True, (255, 220, 50))
    surface.blit(rendered, rendered.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))


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

font_sm     = pygame.font.SysFont("Arial", 20, bold=True)
font_big    = pygame.font.SysFont("Arial", 72, bold=True)
f1          = Fighter("p1", start_pos=p1Pos, facing=1)
f2          = Fighter("p2", start_pos=p2Pos, facing=-1)
prev_attack = {"p1": False, "p2": False}
game_over   = False
winner_text = ""

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

    dt  = clock.get_time() / 1000.0
    now = pygame.time.get_ticks() / 1000.0

    p1_attack = keys[pygame.K_w]
    p2_attack = keys[pygame.K_o]

    if not game_over:
        if p1_attack and not prev_attack["p1"]:
            f1.try_attack(now, back_held=keys[pygame.K_a], fwd_held=keys[pygame.K_d])
        if p2_attack and not prev_attack["p2"]:
            f2.try_attack(now, back_held=keys[pygame.K_RIGHT], fwd_held=keys[pygame.K_LEFT])

        prev_attack["p1"] = p1_attack
        prev_attack["p2"] = p2_attack

        # sync Fighter positions with p1Pos/p2Pos
        f1.pos.x = p1Pos.x
        f2.pos.x = p2Pos.x

        f1.update(dt, keys[pygame.K_a], keys[pygame.K_d], now, opponent=f2)
        f2.update(dt, keys[pygame.K_LEFT], keys[pygame.K_RIGHT], now, opponent=f1)

        if not f1.attacking and not f1.hurting and not f1.dead:
            f1.facing = 1 if f2.pos.x > f1.pos.x else -1
        if not f2.attacking and not f2.hurting and not f2.dead:
            f2.facing = 1 if f1.pos.x > f2.pos.x else -1

        if f1.dead:
            game_over, winner_text = True, "Player 2  WINS!"
        elif f2.dead:
            game_over, winner_text = True, "Player 1  WINS!"

    draw_hp_bars(screen, f1, f2, font_sm)
    if game_over:
        draw_win_screen(screen, winner_text, font_big)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()