import pygame
import sys
import random
import os
from abc import ABC, abstractmethod

# --- CONFIGURATION GLOBALE ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

GRAVITY = 0.5
JUMP_STRENGTH = -8

# --- CONSTANTES FICHIERS & EVENTS ---
CLOUD_SPAWN = pygame.USEREVENT + 1
PIPE_SPAWN = pygame.USEREVENT

CLOUD_IMAGE_PATH = "cloud.png"
PLAYER_IMAGE_PATH = "flappy-bird-character-artwork-u3uhvs4cwrwrndie.png"
PIPE_IMAGE_PATH = "tuyau.png" 

# --- GESTION SAUVEGARDE (High Score) ---
if not os.path.exists("sauvegarde.txt"):
    with open("sauvegarde.txt", "w") as f:
        f.write("0")

with open("sauvegarde.txt", "r") as fichier:
    try:
        high_score = int(fichier.read())
    except:
        high_score = 0

# --- INITIALISATION PYGAME ---
pygame.init()

# Initialisation des polices
font_game_over = pygame.font.SysFont('Arial', 50, bold=True)
font_restart = pygame.font.SysFont('Arial', 30)
police_score = pygame.font.Font(None, 50)

# Timers
pygame.time.set_timer(PIPE_SPAWN, 1500)
pygame.time.set_timer(CLOUD_SPAWN, random.randint(2000, 4000))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Oiseau Battant Ultime 2000")
clock = pygame.time.Clock()

# --- CHARGEMENT DES IMAGES GLOBALES ---
try:
    pipe_img_original = pygame.image.load(PIPE_IMAGE_PATH).convert_alpha()
except FileNotFoundError:
    pipe_img_original = None
    print(f"ATTENTION : '{PIPE_IMAGE_PATH}' introuvable. Les tuyaux seront verts.")

# --- CLASSES ---

class GameObject(ABC):
    @abstractmethod
    def update(self):
        pass

class Cloud(GameObject):
    def __init__(self, screen_width, screen_height):
        self.speed = random.uniform(0.5, 1.5) * -1 
        self.y = random.randint(0, screen_height // 2)
        self.x = screen_width + random.randint(10, 100)

        self.using_placeholder = False
        try:
            original_image = pygame.image.load(CLOUD_IMAGE_PATH).convert_alpha()
            scale_factor = random.uniform(0.25, 0.6)
            new_width = int(original_image.get_width() * scale_factor)
            new_height = int(original_image.get_height() * scale_factor)
            self.image = pygame.transform.scale(original_image, (new_width, new_height))
            self.image.set_alpha(random.randint(150, 230))
        except FileNotFoundError:
            self.using_placeholder = True
            self.width = random.randint(60, 120)
            self.height = random.randint(30, 50)
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (255, 255, 255, 180), (0, 0, self.width, self.height))
            pygame.draw.ellipse(self.image, (255, 255, 255, 180), (self.width//4, -5, self.width//2, self.height))

    def update(self):
        self.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Pipe(GameObject):
    GAP_SIZE = 140 
    WIDTH = 60

    def __init__(self, x_pos, screen_height):
        self.x = x_pos
        self.velocity_x = -3
        self.passed = False # <--- NOUVEAU : Indique si le joueur a passé ce tuyau
        
        min_y = 50 + self.GAP_SIZE // 2
        max_y = screen_height - 50 - self.GAP_SIZE // 2
        self.gap_center_y = random.randint(min_y, max_y)

        # Haut
        top_height = self.gap_center_y - self.GAP_SIZE // 2
        self.rect_top = pygame.Rect(self.x, 0, self.WIDTH, top_height)
        self.image_top = None
        if pipe_img_original:
            scaled_img = pygame.transform.scale(pipe_img_original, (self.WIDTH, top_height))
            self.image_top = pygame.transform.flip(scaled_img, False, True)

        # Bas
        bottom_y = self.gap_center_y + self.GAP_SIZE // 2
        bottom_height = screen_height - bottom_y
        self.rect_bottom = pygame.Rect(self.x, bottom_y, self.WIDTH, bottom_height)
        self.image_bottom = None
        if pipe_img_original:
            self.image_bottom = pygame.transform.scale(pipe_img_original, (self.WIDTH, bottom_height))
        
    def update(self):
        self.x += self.velocity_x
        self.rect_top.x = self.x
        self.rect_bottom.x = self.x
        
    def draw(self, screen):
        if pipe_img_original:
            if self.image_top: screen.blit(self.image_top, self.rect_top)
            if self.image_bottom: screen.blit(self.image_bottom, self.rect_bottom)
        else:
            pygame.draw.rect(screen, (0, 200, 50), self.rect_top)
            pygame.draw.rect(screen, (0, 200, 50), self.rect_bottom)
            pygame.draw.rect(screen, (0, 80, 0), self.rect_top, 3)
            pygame.draw.rect(screen, (0, 80, 0), self.rect_bottom, 3)

class Player(GameObject):
    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        self.velocity_y = 0
        self.angle = 0
        self.start_x = x
        self.start_y = y
        
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (40, 30))
            self.image = self.original_image
        except FileNotFoundError:
            self.original_image = pygame.Surface((40, 30))
            self.original_image.fill((255, 0, 0))
            self.image = self.original_image

        self.rect = self.image.get_rect(center=(x, y))

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.velocity_y = 0
        self.angle = 0
        self.rect.center = (int(self.x), int(self.y))
        self.image = self.original_image

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        
    def jump(self):
        self.velocity_y = JUMP_STRENGTH
    
    def update(self):
        self.apply_gravity()
        self.y += self.velocity_y
        self.rect.center = (int(self.x), int(self.y))
        
        if self.y > SCREEN_HEIGHT - self.rect.height // 2:
            self.y = SCREEN_HEIGHT - self.rect.height // 2
            self.velocity_y = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0

        target_angle = -self.velocity_y * 3
        self.angle += (target_angle - self.angle) * 0.1 
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# --- FONCTIONS JEU ---

def check_collision(player, pipes):
    for pipe in pipes:
        # --- CORRECTION HITBOX ---
        # .inflate(-W, -H) réduit la taille du rectangle considéré pour le choc.
        # On réduit la largeur de 25 pixels et la hauteur de 15 pixels.
        # Cela permet d'ignorer les pixels transparents autour de l'oiseau.
        hitbox_player = player.rect.inflate(-25, -15)
        
        # On réduit aussi légèrement la hitbox des tuyaux sur les côtés (-10)
        # pour être plus permissif et rendre le jeu plus agréable.
        hitbox_pipe_top = pipe.rect_top.inflate(-10, 0)
        hitbox_pipe_bottom = pipe.rect_bottom.inflate(-10, 0)
        
        # On vérifie la collision avec ces nouvelles "hitboxes" réduites
        if hitbox_player.colliderect(hitbox_pipe_top) or hitbox_player.colliderect(hitbox_pipe_bottom):
            return True
            
    return False

def draw_game_over(screen):
    # Fond semi-transparent
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0,0))
    
    text_surf = font_game_over.render("GAME OVER", True, (255, 50, 50))
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30))
    screen.blit(text_surf, text_rect)
    
    restart_surf = font_restart.render("Appuyez sur ESPACE pour rejouer", True, (255, 255, 255))
    restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30))
    screen.blit(restart_surf, restart_rect)

# --- BOUCLE PRINCIPALE ---

player = Player(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, PLAYER_IMAGE_PATH)
pipe_list = []
cloud_list = []
score = 0

# Pré-remplissage nuages
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
                    # RESTART
                    game_active = True
                    pipe_list.clear()
                    player.reset()
                    score = 0
            
        if event.type == PIPE_SPAWN and game_active:
            new_pipe = Pipe(SCREEN_WIDTH, SCREEN_HEIGHT)
            pipe_list.append(new_pipe)
            # NOTE : On a retiré l'augmentation du score ici !
        
        if event.type == CLOUD_SPAWN and game_active:
            new_cloud = Cloud(SCREEN_WIDTH, SCREEN_HEIGHT)
            cloud_list.append(new_cloud)
            pygame.time.set_timer(CLOUD_SPAWN, random.randint(2000, 5000))

    screen.fill((135, 206, 235))
    
    if game_active:
        player.update()
        
        # Nuages
        clouds_to_remove = []
        for cloud in cloud_list:
            cloud.update()
            cloud.draw(screen)
            if cloud.x < -1000: clouds_to_remove.append(cloud)
        for c in clouds_to_remove: cloud_list.remove(c)
        
        # Tuyaux
        pipes_to_remove = []
        for pipe in pipe_list:
            pipe.update()
            pipe.draw(screen)
            
            # --- LOGIQUE DE SCORE ---
            # Si le joueur n'a pas encore passé ce tuyau ET que le joueur a dépassé le tuyau
            if not pipe.passed and player.rect.left > pipe.rect_top.right:
                pipe.passed = True
                score += 1
                if score > high_score:
                    high_score = score
                    # Sauvegarde auto
                    with open("sauvegarde.txt", "w") as f:
                        f.write(str(high_score))
            # ------------------------

            if pipe.x + pipe.WIDTH < 0: pipes_to_remove.append(pipe)
        
        for p in pipes_to_remove: pipe_list.remove(p)

        player.draw(screen)

        if check_collision(player, pipe_list) or player.rect.top < 0 or player.rect.bottom >= SCREEN_HEIGHT:
            game_active = False
            
    else:
        for cloud in cloud_list: cloud.draw(screen)
        for pipe in pipe_list: pipe.draw(screen)
        player.draw(screen)
        draw_game_over(screen)

    texte_surface = police_score.render(f"Score: {score} | High Score: {high_score}", True, (255, 255, 255))
    screen.blit(texte_surface, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()