import pygame
import random
import competences

# Constantes
GRID_SIZE = 16   # Nombre de cases
CELL_SIZE = 30   # Taille d'une case
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

BEIGE = (240,210,180)
GREY = (200,200,200)



class Unit:
    """
    Classe pour représenter une unité.

    ...
    Attributs
    ---------
    x : int
        La position x de l'unité sur la grille.
    y : int
        La position y de l'unité sur la grille.
    health : int
        La santé de l'unité.
    health_max : int                    ###################################
        La santé maximale de l'unité 
    attack_power : int
        La puissance d'attaque de l'unité.
    team : str
        L'équipe de l'unité ('player' ou 'enemy').
    is_selected : bool
        Si l'unité est sélectionnée ou non.

    Méthodes
    --------
    move(dx, dy)
        Déplace l'unité de dx, dy.
    attack(target)
        Attaque une unité cible.
    draw(screen)
        Dessine l'unité sur la grille.
    """

    def __init__(self, x, y, health, attack_power, team):
        """
        Construit une unité avec une position, une santé, une puissance d'attaque et une équipe.

        Paramètres
        ----------
        x : int
            La position x de l'unité sur la grille.
        y : int
            La position y de l'unité sur la grille.
        health : int
            La santé de l'unité.
        attack_power : int
            La puissance d'attaque de l'unité.
        team : str
            L'équipe de l'unité ('player' ou 'enemy').
        """
        self.x = x
        self.y = y
        self.health = health
        self.__health_max = health  # *H*
        self.attack_power = attack_power
        self.team = team  # 'player' ou 'enemy'
        self.is_selected = False
        
    # *H* -->
    @property
    def health_max(self):   
        return self.__health_max
    
    def move(self, dx, dy):
        """Déplace l'unité de dx, dy."""
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx
            self.y += dy

    def attack(self, target):
        """Attaque une unité cible."""
        if abs(self.x - target.x) <= 1 and abs(self.y - target.y) <= 1:
            target.health -= self.attack_power

    def draw(self, screen):
        """Affiche l'unité sur l'écran."""
        color = BLUE if self.team == 'player' else RED
        if self.is_selected:
            pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE,
                             self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.circle(screen, color, (self.x * CELL_SIZE + CELL_SIZE //
                           2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
        
# Test Hadriel:
class Canard(Unit):
    def draw(self,screen):
        canard = pygame.image.load("canard.png")
        if self.is_selected:
            canard = pygame.image.load("canard.png")
            canard = pygame.transform.scale(canard, (CELL_SIZE, CELL_SIZE)) # redimensionner l'image
            screen.blit(canard,(self.x * CELL_SIZE,self.y * CELL_SIZE)) # afficher l'image

class guerrier(Unit):
    def __init__(self, x, y, health, attack_power, team):
        super().__init__(x, y, health, attack_power, team)
        self.competences = competences.Spin()
class archer(Unit):
    def __init__(self, x, y, health, attack_power, team):
        super().__init__(x, y, health, attack_power, team)
        self.competences = competences.Tir()
class mage(Unit):
    def __init__(self, x, y, health, attack_power, team):
        super().__init__(x, y, health, attack_power, team)#x,y,60,20,team
        self.competences = competences.BouleDeFeu()
class paladin(Unit):
    def __init__(self, x, y, health, attack_power, team):
        super().__init__(x, y, health, attack_power, team)
        self.competences = competences.Soin()
