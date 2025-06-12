import pygame
import random
import math
import os

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 5
ENEMY_SPEED = 2
SHOOT_COOLDOWN = 500
ENEMY_SHOOT_INTERVAL = 1500
PLAYER_HEALTH = 100
ENEMY_HEALTH = 50
WAVES = [3, 5, 8, 10, 15]

# Paths
ASSET_PATH = "assets"
BACKGROUND_IMAGE = os.path.join(ASSET_PATH, "ny_street.jpg")
PLAYER_IMAGE = os.path.join(ASSET_PATH, "player.jpg")
ENEMY_IMAGE = os.path.join(ASSET_PATH, "hobo.jpg")

# Init
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NYC Shooter")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load and Tint Images
def tint_image(image, color):
    tinted = image.copy()
    tinted.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

background = pygame.transform.scale(pygame.image.load(BACKGROUND_IMAGE), (WIDTH, HEIGHT))

player_sprite_raw = pygame.transform.scale(pygame.image.load(PLAYER_IMAGE), (60, 60))
player_sprite = tint_image(player_sprite_raw.convert_alpha(), (200, 160, 255))  # Light purple

enemy_sprite = pygame.transform.scale(pygame.image.load(ENEMY_IMAGE), (50, 50))  # No tint

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_sprite
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.health = PLAYER_HEALTH
        self.last_shot = 0

    def update(self, keys):
        dx = dy = 0
        if keys[pygame.K_w]: dy -= PLAYER_SPEED
        if keys[pygame.K_s]: dy += PLAYER_SPEED
        if keys[pygame.K_a]: dx -= PLAYER_SPEED
        if keys[pygame.K_d]: dx += PLAYER_SPEED
        self.rect.move_ip(dx, dy)
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self, bullets_group):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= SHOOT_COOLDOWN:
            bullet = Bullet(self.rect.center, pygame.mouse.get_pos(), BULLET_SPEED, (255, 255, 0))
            bullets_group.add(bullet)
            self.last_shot = now

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((52, 52), pygame.SRCALPHA)
        self.sprite = enemy_sprite
        self.rect = self.image.get_rect(
            center=(random.randint(60, WIDTH - 60), random.randint(60, HEIGHT - 60))
        )
        self.health = ENEMY_HEALTH
        self.last_shot = pygame.time.get_ticks()
        self.draw_with_border()

    def draw_with_border(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, (255, 0, 0), (0, 0, 52, 52), 2)
        self.image.blit(self.sprite, (1, 1))

    def update(self, player_pos, enemy_bullets):
        dx, dy = player_pos[0] - self.rect.centerx, player_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx, dy = dx / dist, dy / dist
            self.rect.move_ip(dx * ENEMY_SPEED, dy * ENEMY_SPEED)

        now = pygame.time.get_ticks()
        if now - self.last_shot > ENEMY_SHOOT_INTERVAL:
            bullet = Bullet(self.rect.center, player_pos, ENEMY_BULLET_SPEED, (200, 0, 0))
            enemy_bullets.add(bullet)
            self.last_shot = now

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, speed, color):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (5, 5), 5)
        self.rect = self.image.get_rect(center=start_pos)
        dx, dy = target_pos[0] - start_pos[0], target_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy)
        self.velocity = (dx / dist * speed, dy / dist * speed)

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not screen.get_rect().collidepoint(self.rect.center):
            self.kill()

# Groups
player = Player()
player_group = pygame.sprite.Group(player)
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Game State
wave_index = 0
def spawn_wave(n):
    return pygame.sprite.Group(Enemy() for _ in range(n))

enemies = spawn_wave(WAVES[wave_index])

# Game loop
running = True
while running:
    clock.tick(FPS)
    screen.blit(background, (0, 0))
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.shoot(bullets)

    player.update(keys)
    for enemy in enemies:
        enemy.update(player.rect.center, enemy_bullets)
    bullets.update()
    enemy_bullets.update()

    for bullet in bullets:
        hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
        for enemy in hit_enemies:
            enemy.health -= 25
            bullet.kill()
            if enemy.health <= 0:
                enemy.kill()

    if pygame.sprite.spritecollide(player, enemy_bullets, True):
        player.health -= 10

    player_group.draw(screen)
    enemies.draw(screen)
    bullets.draw(screen)
    enemy_bullets.draw(screen)

    health_text = font.render(f"Health: {player.health}", True, (255, 0, 0))
    wave_text = font.render(f"Wave {wave_index + 1}/5", True, (0, 0, 0))
    screen.blit(health_text, (10, 10))
    screen.blit(wave_text, (10, 50))

    if player.health <= 0:
        msg = font.render("You Died", True, (0, 0, 0))
        screen.blit(msg, (WIDTH // 2 - 60, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    elif len(enemies) == 0:
        wave_index += 1
        if wave_index >= len(WAVES):
            msg = font.render("Victory!", True, (0, 0, 139))
            screen.blit(msg, (WIDTH // 2 - 60, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False
        else:
            enemies = spawn_wave(WAVES[wave_index])

    pygame.display.flip()

pygame.quit()