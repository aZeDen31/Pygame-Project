import pygame
import sys
from abc import ABC, abstractmethod

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

GRAVITY = 0.5
JUMP_STRENGTH = -10


class GameObject(ABC):
    @abstractmethod
    def update(self):
        pass

class Player:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity_y = 0

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        
    def jump(self):
        self.velocity_y = JUMP_STRENGTH
    
    def update(self):
        self.apply_gravity()
        self.y += self.velocity_y
        
        if self.y > SCREEN_HEIGHT - self.radius:
            self.y = SCREEN_HEIGHT - self.radius
            self.velocity_y = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Flappy Physics")
clock = pygame.time.Clock()

player = Player(
    x=SCREEN_WIDTH // 4, 
    y=SCREEN_HEIGHT // 2, 
    radius=20, 
    color=(255, 100, 100)
)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            player.jump()

    player.update()

    screen.fill((50, 50, 50))
    
    player.draw(screen)

    pygame.display.flip()
    
    clock.tick(FPS)

pygame.quit()
sys.exit()