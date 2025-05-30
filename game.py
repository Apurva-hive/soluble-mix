import pygame
import random

# Initialize Pygame
pygame.init()

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Side-Scrolling Shooter")

clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 20)

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Global constants
GRAVITY = 0.8
GROUND_LEVEL = SCREEN_HEIGHT - 50

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(midbottom=(100, GROUND_LEVEL))
        self.speed = 5
        self.velocity_y = 0
        self.jumping = False
        self.health = 100
        self.lives = 3
        self.shoot_cooldown = 0
    
    def update(self, keys_pressed):
        # Horizontal movement
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed
        
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        # Gravity & jump
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        if self.rect.bottom > GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.jumping = False
            self.velocity_y = 0
        
        # Jumping
        if keys_pressed[pygame.K_SPACE] and not self.jumping:
            self.velocity_y = -15
            self.jumping = True
        
        # Shoot cooldown timer
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 20  # cooldown frames
            return Projectile(self.rect.midright)
        return None
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.lives -= 1
            self.health = 100
            self.rect.midbottom = (100, GROUND_LEVEL)
            if self.lives <= 0:
                return True  # Player died
        return False

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=pos)
        self.speed = 10
        self.damage = 25
    
    def update(self):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, is_boss=False):
        super().__init__()
        self.is_boss = is_boss
        if self.is_boss:
            self.image = pygame.Surface((80, 100))
            self.image.fill(RED)
            self.health = 200
            self.speed = 2
        else:
            self.image = pygame.Surface((40, 50))
            self.image.fill(RED)
            self.health = 50
            self.speed = 3
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.direction = -1
    
    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1  # Change direction
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True  # Enemy died
        return False

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.kind = kind  # 'health' or 'life'
        self.image = pygame.Surface((30, 30))
        if kind == 'health':
            self.image.fill(GREEN)
        elif kind == 'life':
            self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))

# Level design and game management
class Level:
    def __init__(self, number):
        self.number = number
        self.enemies = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.boss_spawned = False
        
        # Spawn enemies and collectibles based on level number
        for i in range(5 + number*2):
            enemy_x = random.randint(400, SCREEN_WIDTH - 50)
            enemy = Enemy(enemy_x, GROUND_LEVEL)
            self.enemies.add(enemy)
        
        # Spawn collectibles
        for i in range(3):
            ctype = random.choice(['health', 'life'])
            c = Collectible(random.randint(200, SCREEN_WIDTH - 50), random.randint(100, GROUND_LEVEL - 50), ctype)
            self.collectibles.add(c)
    
    def spawn_boss(self):
        boss = Enemy(SCREEN_WIDTH - 100, GROUND_LEVEL, is_boss=True)
        self.enemies.add(boss)
        self.boss_spawned = True

def draw_health_bar(surface, x, y, health, max_health, width=100, height=10):
    ratio = health / max_health
    pygame.draw.rect(surface, RED, (x, y, width, height))
    pygame.draw.rect(surface, GREEN, (x, y, width * ratio, height))

def draw_text(surface, text, x, y, color=WHITE):
    img = FONT.render(text, True, color)
    surface.blit(img, (x, y))

def game_over_screen(score):
    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", SCREEN_WIDTH//2 - 70, SCREEN_HEIGHT//2 - 30, RED)
    draw_text(screen, f"Final Score: {score}", SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2, WHITE)
    draw_text(screen, "Press R to Restart or Q to Quit", SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 30, WHITE)
    pygame.display.update()

def main():
    player = Player()
    projectiles = pygame.sprite.Group()
    
    current_level_number = 1
    level = Level(current_level_number)
    
    score = 0
    game_over = False
    running = True
    
    while running:
        clock.tick(60)
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        proj = player.shoot()
                        if proj:
                            projectiles.add(proj)
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        main()  # Restart game
                        return
                    elif event.key == pygame.K_q:
                        running = False
        
        if not game_over:
            # Update player
            player.update(keys)
            
            # Update projectiles
            projectiles.update()
            
            # Update enemies
            level.enemies.update()
            
            # Check projectile-enemy collisions
            for proj in projectiles:
                hit_enemies = pygame.sprite.spritecollide(proj, level.enemies, False)
                for enemy in hit_enemies:
                    died = enemy.take_damage(proj.damage)
                    proj.kill()
                    if died:
                        score += 100 if not enemy.is_boss else 500
            
            # Check enemy-player collisions
            enemy_hits = pygame.sprite.spritecollide(player, level.enemies, False)
            for enemy in enemy_hits:
                # Damage player and knock back
                player_died = player.take_damage(10)
                player.rect.x -= 20
                if player_died:
                    game_over = True
            
            # Check player-collectible collisions
            collected = pygame.sprite.spritecollide(player, level.collectibles, True)
            for item in collected:
                if item.kind == 'health':
                    player.health += 30
                    if player.health > 100:
                        player.health = 100
                    score += 50
                elif item.kind == 'life':
                    player.lives += 1
                    score += 100
            
            # Level progression
            if len(level.enemies) == 0 and not level.boss_spawned:
                # Spawn boss
                level.spawn_boss()
            
            # If boss defeated, go to next level or end
            if level.boss_spawned and len(level.enemies) == 0:
                if current_level_number < 3:
                    current_level_number += 1
                    level = Level(current_level_number)
                else:
                    # Game finished
                    game_over = True
            
            # Draw everything
            screen.fill(BLACK)
            screen.blit(player.image, player.rect)
            projectiles.draw(screen)
            level.enemies.draw(screen)
            level.collectibles.draw(screen)
            
            # Draw HUD
            draw_text(screen, f"Score: {score}", 10, 10)
            draw_text(screen, f"Lives: {player.lives}", 10, 35)
            draw_health_bar(screen, 10, 60, player.health, 100)
            
            # Draw enemies health bars
            for enemy in level.enemies:
                draw_health_bar(screen, enemy.rect.x, enemy.rect.y - 10, enemy.health, 200 if enemy.is_boss else 50, enemy.rect.width, 5)
            
            pygame.display.update()
        else:
            game_over_screen(score)
    
    pygame.quit()

if __name__ == "__main__":
    main()
