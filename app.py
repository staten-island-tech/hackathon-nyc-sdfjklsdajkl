# Step 1: Build a minimal top-down shooter in pygame
# Player can move and shoot. Bots chase and shoot. Basic collision and health system.

import pygame
import random
import math

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 2
SHOOT_COOLDOWN = 500  # in milliseconds
ENEMY_SPAWN_COUNT = 5
PLAYER_HEALTH = 100
ENEMY_HEALTH = 50

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NYC Shooter Prototype")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Entities
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 150, 255))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.health = PLAYER_HEALTH
        self.last_shot = 0

    def update(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= PLAYER_SPEED
        if keys[pygame.K_s]: dy += PLAYER_SPEED
        if keys[pygame.K_a]: dx -= PLAYER_SPEED
        if keys[pygame.K_d]: dx += PLAYER_SPEED
        self.rect.move_ip(dx, dy)
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self, bullets_group):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= SHOOT_COOLDOWN:
            bullet = Bullet(self.rect.center, pygame.mouse.get_pos())
            bullets_group.add(bullet)
            self.last_shot = now

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 50, 50))
        self.rect = self.image.get_rect(
            center=(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        )
        self.health = ENEMY_HEALTH

    def update(self, player_pos):
        dx, dy = player_pos[0] - self.rect.centerx, player_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx, dy = dx / dist, dy / dist
            self.rect.move_ip(dx * ENEMY_SPEED, dy * ENEMY_SPEED)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos):
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=start_pos)
        dx, dy = target_pos[0] - start_pos[0], target_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy)
        self.velocity = (dx / dist * BULLET_SPEED, dy / dist * BULLET_SPEED)

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not screen.get_rect().collidepoint(self.rect.center):
            self.kill()

# Groups
player = Player()
player_group = pygame.sprite.Group(player)
enemies = pygame.sprite.Group(Enemy() for _ in range(ENEMY_SPAWN_COUNT))
bullets = pygame.sprite.Group()

# Game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill((30, 30, 30))
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.shoot(bullets)

    # Update
    player.update(keys)
    enemies.update(player.rect.center)
    bullets.update()

    # Check collisions
    for bullet in bullets:
        hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
        for enemy in hit_enemies:
            enemy.health -= 25
            bullet.kill()
            if enemy.health <= 0:
                enemy.kill()

    if pygame.sprite.spritecollide(player, enemies, False):
        player.health -= 1  # lose health on contact

    # Draw
    player_group.draw(screen)
    enemies.draw(screen)
    bullets.draw(screen)

    # HUD
    hp_text = font.render(f"Health: {player.health}", True, (255, 255, 255))
    screen.blit(hp_text, (10, 10))
    enemies_text = font.render(f"Enemies left: {len(enemies)}", True, (255, 255, 255))
    screen.blit(enemies_text, (10, 30))

    # Check win/loss
    if player.health <= 0:
        msg = font.render("You Died", True, (255, 0, 0))
        screen.blit(msg, (WIDTH // 2 - 40, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    elif not enemies:
        msg = font.render("Victory!", True, (0, 255, 0))
        screen.blit(msg, (WIDTH // 2 - 40, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    pygame.display.flip()

pygame.quit()
