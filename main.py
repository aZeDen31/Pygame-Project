import pygame
import sys
from abc import ABC, abstractmethod

# --- Constantes du Jeu ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

# --- Paramètres de la Physique ---
GRAVITY = 0.5    # Vitesse d'accélération de la gravité (plus c'est haut, plus ça tombe vite)
JUMP_STRENGTH = -10 # Force appliquée lors d'un saut (valeur négative car l'axe Y est inversé)

# --- Classe du Personnage (Player) ---

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
        self.velocity_y = 0  # Vitesse verticale initiale

    def apply_gravity(self):
        # La gravité augmente la vitesse verticale à chaque image
        self.velocity_y += GRAVITY
        
    def jump(self):
        # Applique une force négative (vers le haut) pour le saut
        # Cela écrase la vitesse actuelle, permettant des sauts illimités
        self.velocity_y = JUMP_STRENGTH
    
    def update(self):
        # 1. Applique la gravité
        self.apply_gravity()
        
        # 2. Met à jour la position Y
        self.y += self.velocity_y
        
        # 3. Empêche le personnage de tomber sous l'écran
        if self.y > SCREEN_HEIGHT - self.radius:
            self.y = SCREEN_HEIGHT - self.radius
            self.velocity_y = 0 # Arrête le mouvement quand il touche le sol

    def draw(self, screen):
        # Dessine le cercle à sa position actuelle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# --- Initialisation de Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Flappy Physics")
clock = pygame.time.Clock()

# --- Création du Joueur ---
player = Player(
    x=SCREEN_WIDTH // 4, 
    y=SCREEN_HEIGHT // 2, 
    radius=20, 
    color=(255, 100, 100) # Rouge clair
)

# --- Boucle Principale du Jeu ---
running = True
while running:
    # --- Gestion des Événements ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Gère le saut (n'importe quelle touche enfoncée)
        if event.type == pygame.KEYDOWN:
            # Pour un comportement similaire à Flappy Bird :
            # Chaque pression de touche déclenche un saut
            player.jump()

    # --- Logique de Jeu (Mise à jour de la Physique) ---
    player.update() # Ceci appelle apply_gravity() et met à jour la position Y

    # --- Dessin (Rendu) ---
    screen.fill((50, 50, 50)) # Fond gris foncé
    
    player.draw(screen)

    # --- Mise à jour de l'Affichage ---
    pygame.display.flip()
    
    # Limite les images par seconde
    clock.tick(FPS)

pygame.quit()
sys.exit()