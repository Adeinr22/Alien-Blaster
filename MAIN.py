#===============================================================================#
# Spaceship Game (MAIN.py)
# Developed by: Andrei Jules V. Dela Cruz
# Date Created: February 22, 2026
# Last Update:
#===============================================================================#
import pygame
from random import randint, uniform
from os.path import join

# ---------- Game State ----------
game_state = "START"          # "START", "PLAYING", "GAME_OVER"
game_start_time = 0
final_score = 0

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('Images', 'Player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (window_width / 2, window_height / 2))
        self.direction = pygame.math.Vector2()
        self.speed = 500

        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 300

        self.mask = pygame.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surface, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        self.laser_timer()

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.speed = 500
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.orinal_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 500)
        self.rotation_speed = randint(40,80)
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.orinal_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
    
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index) % len(self.frames)]
        else:
            self.kill()

def collisions():
    global game_state, final_score

    if player is None:
        return

    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        # Player hit → game over
        AnimatedExplosion(explosion_frames, player.rect.center, all_sprites)
        explosion_sound.play()
        player.kill()
        final_score = (pygame.time.get_ticks() - game_start_time) // 100
        game_state = "GAME_OVER"
        return

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True, pygame.sprite.collide_mask)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()

def display_score():
    if game_state == "PLAYING":
        current_time = (pygame.time.get_ticks() - game_start_time) // 100
    else:
        current_time = final_score
    text_surface = font.render(str(current_time), True, 'white')
    text_rect = text_surface.get_frect(midbottom = (window_width / 2, window_height - 50))
    display_surface.blit(text_surface, text_rect)
    pygame.draw.rect(display_surface,'white', text_rect.inflate(20,30), 5, 10)

def draw_start_screen():
    # Draw background (stars are already drawn via all_sprites)
    title = font.render("Alien Blaster", True, 'white')
    title_rect = title.get_frect(center=(window_width/2, window_height/2 - 50))
    display_surface.blit(title, title_rect)

    instruction = pygame.font.Font('Oxanium-Bold.ttf', 30).render("Press SPACE to start", True, 'white')
    instr_rect = instruction.get_frect(center=(window_width/2, window_height/2 + 20))
    display_surface.blit(instruction, instr_rect)

def draw_game_over_screen():
    game_over = font.render("GAME OVER", True, 'red')
    game_over_rect = game_over.get_frect(center=(window_width/2, window_height/2 - 50))
    display_surface.blit(game_over, game_over_rect)

    score_text = pygame.font.Font('Oxanium-Bold.ttf', 30).render(f"Score: {final_score}", True, 'white')
    score_rect = score_text.get_frect(center=(window_width/2, window_height/2 + 10))
    display_surface.blit(score_text, score_rect)

    restart_text = pygame.font.Font('Oxanium-Bold.ttf', 30).render("Press SPACE to continue", True, 'white')
    restart_rect = restart_text.get_frect(center=(window_width/2, window_height/2 + 60))
    display_surface.blit(restart_text, restart_rect)

def reset_game():
    global player, game_start_time, final_score, game_state
    # Clear existing enemies and lasers
    meteor_sprites.empty()
    laser_sprites.empty()
    # Remove old player if exists
    if player:
        player.kill()
    # Create new player
    player = Player(all_sprites)
    # Reset timer
    game_start_time = pygame.time.get_ticks()
    final_score = 0
    game_state = "PLAYING"

# ---------- General Setup ----------
pygame.init()
window_width, window_height = 1280, 720 
display_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Alien Blaster")
running = True
clock = pygame.time.Clock()

# Imports
meteor_surface = pygame.image.load(join('Images','meteor.png')).convert_alpha()
laser_surface = pygame.image.load(join('Images','laser.png')).convert_alpha()
background = pygame.image.load(join('Images', 'background.png')).convert()
font = pygame.font.Font('Oxanium-Bold.ttf', 50)
explosion_frames = [pygame.image.load(join('Images', 'Explosions', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(1)
game_music.play(loops=-1)

# Sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group() 

# Player starts as None; will be created when game starts
player = None

# Custom events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 200)

# ---------- Main Loop ----------
while running:
    dt = clock.tick() / 1000

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event and game_state == "PLAYING":
            x, y = randint(0, window_width), randint(-200, -100)
            Meteor(meteor_surface, (x, y), (all_sprites, meteor_sprites))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == "START":
                    reset_game()
                elif game_state == "GAME_OVER":
                    # Go back to start screen
                    game_state = "START"
                    # Clear remaining sprites (except stars)
                    meteor_sprites.empty()
                    laser_sprites.empty()
                    if player:
                        player.kill()
                        player = None

    # Update logic based on state
    if game_state == "PLAYING":
        all_sprites.update(dt)
        collisions()

    # Drawing
    display_surface.blit(background, (0, 0))
    all_sprites.draw(display_surface)
    display_score()

    # State-specific overlays
    if game_state == "START":
        draw_start_screen()
    elif game_state == "GAME_OVER":
        draw_game_over_screen()

    pygame.display.update()

pygame.quit()