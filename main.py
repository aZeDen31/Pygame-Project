import pygame
import sys
import random
from abc import ABC, abstractmethod

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

GRAVITY = 0.5
JUMP_STRENGTH = -8

PIPE_SPAWN = pygame.USEREVENT

with open("sauvegarde.txt", "r") as fichier:
    high_score = fichier.read()

pygame.init()

pygame.time.set_timer(PIPE_SPAWN, 1500)

police = pygame.font.Font(None, 50)

class GameObject(ABC):
    @abstractmethod
    def update(self):
        pass

class Pipe (GameObject):
    GAP_SIZE = 120
    WIDTH = 50

    def __init__(self, x_pos, screen_height):
        self.x = x_pos
        self.velocity_x = -3
        
        min_y = 50 + self.GAP_SIZE // 2
        max_y = screen_height - 50 - self.GAP_SIZE // 2
        self.gap_center_y = random.randint(min_y, max_y)

        top_height = self.gap_center_y - self.GAP_SIZE // 2
        self.rect_top = pygame.Rect(self.x, 0, self.WIDTH, top_height)

        bottom_y = self.gap_center_y + self.GAP_SIZE // 2
        bottom_height = screen_height - bottom_y
        self.rect_bottom = pygame.Rect(self.x, bottom_y, self.WIDTH, bottom_height)
        
    def update(self):
        self.x += self.velocity_x
        self.rect_top.x = self.x
        self.rect_bottom.x = self.x
        
    def draw(self, screen):
        pygame.draw.rect(screen, (0, 200, 50), self.rect_top)
        pygame.draw.rect(screen, (0, 200, 50), self.rect_bottom)

class Player(GameObject):
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity_y = 0
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        
    def jump(self):
        self.velocity_y = JUMP_STRENGTH
    
    def update(self):
        self.apply_gravity()
        self.y += self.velocity_y
        self.rect.center = (int(self.x), int(self.y))
        
        if self.y > SCREEN_HEIGHT - self.radius:
            self.y = SCREEN_HEIGHT - self.radius
            self.velocity_y = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def check_collision(player, pipes):
    for pipe in pipes:
        if player.rect.colliderect(pipe.rect_top) or player.rect.colliderect(pipe.rect_bottom):
            return True
    return False


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Flappy Physics")
clock = pygame.time.Clock()

player = Player(
    x=SCREEN_WIDTH // 4, 
    y=SCREEN_HEIGHT // 2, 
    radius=20, 
    color=(255, 100, 100)
)

pipe_list = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            player.jump()
            
        if event.type == PIPE_SPAWN:
            new_pipe = Pipe(SCREEN_WIDTH, SCREEN_HEIGHT)
            pipe_list.append(new_pipe)

    if check_collision(player, pipe_list): 
        print("GAME OVER! Collision!")
        running = False

    player.update()
    
    pipes_to_remove = []
    for pipe in pipe_list:
        pipe.update()
        if pipe.x + pipe.WIDTH < 0:
            pipes_to_remove.append(pipe)
            
    for pipe in pipes_to_remove:
        pipe_list.remove(pipe)

    screen.fill((50, 50, 50))
    
    for pipe in pipe_list:
        pipe.draw(screen)
        
    player.draw(screen)

    pygame.display.flip()    

    texte_surface = police.render(f"Score : {high_score}", True, (255, 255, 255))
    
    clock.tick(FPS)

pygame.quit()
sys.exit() 