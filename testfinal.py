import pygame
import sys
import random
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

GRAVITY = 0.5
JUMP_STRENGTH = -8

CLOUD_SPAWN = pygame.USEREVENT + 1
PIPE_SPAWN = pygame.USEREVENT

CLOUD_IMAGE_PATH = "cloud.png"
PLAYER_IMAGE_PATH = "flappy-bird-character-artwork-u3uhvs4cwrwrndie.png"
PIPE_IMAGE_PATH = "tuyau.png" 

if not os.path.exists("sauvegarde.txt"):
    with open("sauvegarde.txt", "w") as f:
        f.write("0")

with open("sauvegarde.txt", "r") as fichier:
    try:
        high_score = int(fichier.read())
    except:
        high_score = 0

pygame.init()

font_game_over = pygame.font.SysFont('Arial', 50, bold=True)
font_restart = pygame.font.SysFont('Arial', 30)
police_score = pygame.font.Font(None, 50)

pygame.time.set_timer(PIPE_SPAWN, 1500)
pygame.time.set_timer(CLOUD_SPAWN, random.randint(2000, 4000))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Oiseau Battant Ultime 2000")
clock = pygame.time.Clock()

class Entity:
    def __init__(self, x, y, image_path=None, width=0, height=0, color=(255, 0, 255)):
        self.x = x
        self.y = y
        self.image = None
        self.rect = None
        
        if image_path and os.path.exists(image_path):
            try:
                loaded_img = pygame.image.load(image_path).convert_alpha()
                if width > 0 and height > 0:
                    self.image = pygame.transform.scale(loaded_img, (width, height))
                else:
                    self.image = loaded_img
            except:
                pass

        if self.image is None:
            w = width if width > 0 else 50
            h = height if height > 0 else 50
            self.image = pygame.Surface((w, h))
            self.image.fill(color)

        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        pass

    def draw(self, screen):
        self.rect.topleft = (int(self.x), int(self.y))
        screen.blit(self.image, self.rect)

class Cloud(Entity):
    def __init__(self, screen_width, screen_height):
        x = screen_width + random.randint(10, 100)
        y = random.randint(0, screen_height // 2)
        
        super().__init__(x, y, CLOUD_IMAGE_PATH)
        
        self.speed = random.uniform(0.5, 1.5) * -1
        
        scale_factor = random.uniform(0.25, 0.6)
        if CLOUD_IMAGE_PATH and os.path.exists(CLOUD_IMAGE_PATH):
            w = int(self.image.get_width() * scale_factor)
            h = int(self.image.get_height() * scale_factor)
            self.image = pygame.transform.scale(self.image, (w, h))
        else:
            w = random.randint(60, 120)
            h = random.randint(30, 50)
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (255, 255, 255, 180), (0, 0, w, h))

        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.x += self.speed

class PipeSegment(Entity):
    def __init__(self, x, y, width, height, is_top):
        super().__init__(x, y, PIPE_IMAGE_PATH, width, height, color=(0, 200, 50))
        if is_top and os.path.exists(PIPE_IMAGE_PATH):
            self.image = pygame.transform.flip(self.image, False, True)
    
    def update_position(self, x):
        self.x = x

class PipeManager:
    GAP_SIZE = 140 
    WIDTH = 60

    def __init__(self, start_x, screen_height):
        self.x = start_x
        self.screen_height = screen_height
        self.velocity_x = -3
        self.passed = False
        
        min_y = 50 + self.GAP_SIZE // 2
        max_y = screen_height - 50 - self.GAP_SIZE // 2
        gap_center_y = random.randint(min_y, max_y)

        top_height = gap_center_y - self.GAP_SIZE // 2
        self.top_pipe = PipeSegment(self.x, 0, self.WIDTH, top_height, True)
        
        bottom_y = gap_center_y + self.GAP_SIZE // 2
        bottom_height = screen_height - bottom_y
        self.bottom_pipe = PipeSegment(self.x, bottom_y, self.WIDTH, bottom_height, False)

    def update(self):
        self.x += self.velocity_x
        self.top_pipe.update_position(self.x)
        self.bottom_pipe.update_position(self.x)

    def draw(self, screen):
        self.top_pipe.draw(screen)
        self.bottom_pipe.draw(screen)

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_IMAGE_PATH, 40, 30, color=(255, 0, 0))
        self.start_x = x
        self.start_y = y
        self.velocity_y = 0
        self.angle = 0
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(x, y))

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.velocity_y = 0
        self.angle = 0
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def jump(self):
        self.velocity_y = JUMP_STRENGTH
    
    def update(self):
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        
        if self.y > SCREEN_HEIGHT - self.rect.height // 2:
            self.y = SCREEN_HEIGHT - self.rect.height // 2
            self.velocity_y = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0

        target_angle = -self.velocity_y * 3
        self.angle += (target_angle - self.angle) * 0.1 
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

def check_collision(player, pipe_managers):
    hitbox_player = player.rect.inflate(-25, -15)
    
    for pm in pipe_managers:
        hitbox_top = pm.top_pipe.rect.inflate(-10, 0)
        hitbox_bottom = pm.bottom_pipe.rect.inflate(-10, 0)
        
        if hitbox_player.colliderect(hitbox_top) or hitbox_player.colliderect(hitbox_bottom):
            return True
    return False

def draw_game_over(screen):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0,0))
    
    text_surf = font_game_over.render("GAME OVER", True, (255, 50, 50))
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30))
    screen.blit(text_surf, text_rect)
    
    restart_surf = font_restart.render("Appuyez sur ESPACE pour rejouer", True, (255, 255, 255))
    restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30))
    screen.blit(restart_surf, restart_rect)

player = Player(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
pipe_list = []
cloud_list = []
score = 0

for _ in range(3):
    c = Cloud(SCREEN_WIDTH, SCREEN_HEIGHT)
    c.x = random.randint(0, SCREEN_WIDTH)
    cloud_list.append(c)

running = True
game_active = True 

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                if game_active:
                    player.jump()
                else:
                    game_active = True
                    pipe_list.clear()
                    player.reset()
                    score = 0
            
        if event.type == PIPE_SPAWN and game_active:
            new_pipe = PipeManager(SCREEN_WIDTH, SCREEN_HEIGHT)
            pipe_list.append(new_pipe)
        
        if event.type == CLOUD_SPAWN and game_active:
            new_cloud = Cloud(SCREEN_WIDTH, SCREEN_HEIGHT)
            cloud_list.append(new_cloud)
            pygame.time.set_timer(CLOUD_SPAWN, random.randint(2000, 5000))

    screen.fill((135, 206, 235))
    
    if game_active:
        player.update()
        
        clouds_to_remove = []
        for cloud in cloud_list:
            cloud.update()
            cloud.draw(screen)
            if cloud.x < -1000: clouds_to_remove.append(cloud)
        for c in clouds_to_remove: cloud_list.remove(c)
        
        pipes_to_remove = []
        for pm in pipe_list:
            pm.update()
            pm.draw(screen)
            
            if not pm.passed and player.rect.left > pm.top_pipe.rect.right:
                pm.passed = True
                score += 1
                if score > high_score:
                    high_score = score
                    with open("sauvegarde.txt", "w") as f:
                        f.write(str(high_score))

            if pm.x + pm.WIDTH < 0: pipes_to_remove.append(pm)
        
        for p in pipes_to_remove: pipe_list.remove(p)

        player.draw(screen)

        if check_collision(player, pipe_list) or player.rect.top < 0 or player.rect.bottom >= SCREEN_HEIGHT:
            game_active = False
            
    else:
        for cloud in cloud_list: cloud.draw(screen)
        for pm in pipe_list: pm.draw(screen)
        player.draw(screen)
        draw_game_over(screen)

    texte_surface = police_score.render(f"Score: {score} | High Score: {high_score}", True, (255, 255, 255))
    screen.blit(texte_surface, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()