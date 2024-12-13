import pygame
import random
import competences

# Constantes
GRID_SIZE = 13   # Nombre de cases
CELL_SIZE = 55   # Taille d'une case
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (150, 0, 200)
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

    def __init__(self, x, y, health, attack_power, speed, team):
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
        self.__health_max = health 
        self.attack_power = attack_power
        self.team = team  # 'player' ou 'enemy'
        self.is_selected = False

        self.speed = speed
        self.pos_debut_tour = (x, y)  # Position au début du tour
        self.cases_acces = set()  # Zone atteignable précalculée

    @property
    def health_max(self):   
        return self.__health_max
    
    def calcule_zone_mov(self):
        """
        Précalcule la zone accessible depuis la position actuelle.
        """
        self.cases_acces = set()
        for x in range(self.pos_debut_tour[0] - self.speed, self.pos_debut_tour[0] + self.speed + 1):
            for y in range(self.pos_debut_tour[1] - self.speed, self.pos_debut_tour[1] + self.speed + 1):
                if (0 <= x < WIDTH // CELL_SIZE and
                    0 <= y < HEIGHT // CELL_SIZE and
                    abs(x - self.pos_debut_tour[0]) + abs(y - self.pos_debut_tour[1]) <= self.speed):
                    self.cases_acces.add((x, y))

    def move(self, dx, dy, murs):
        """
        Déplace l'unité de dx, dy si la position est atteignable.
        """
        new_x, new_y = self.x + dx, self.y + dy
        can_move_to = (new_x, new_y) in self.cases_acces # Vérification avec la zone précalculée
        if can_move_to:  
            mur_ok = False
            for mur in murs:                     
                if mur.effect(self, dx, dy):  # Si l'unité rencontre un mur
                    mur_ok = True
                    break
            if not mur_ok:  # Si aucun mur n'empêche le mouvement
                self.x = new_x
                self.y = new_y

    def attack(self, target):
        """Attaque une unité cible."""
        if abs(self.x - target.x) <= 1 and abs(self.y - target.y) <= 1:
            target.health -= self.attack_power

    def draw(self, screen):
        """Affiche l'unité sur l'écran."""
        if self.is_selected:
            pygame.draw.circle(screen, GREEN, (self.x * CELL_SIZE + CELL_SIZE //
                                2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
        picture = pygame.image.load(self.image)
        picture = pygame.transform.scale(picture, (CELL_SIZE, CELL_SIZE)) # redimensionner l'image
        screen.blit(picture,(self.x * CELL_SIZE,self.y * CELL_SIZE)) # afficher l'image
        
        # Barre de santé
        pygame.draw.rect(screen, PURPLE, (self.x * CELL_SIZE,self.y * CELL_SIZE - 3, round(CELL_SIZE * self.health/self.health_max), 6 ))
        pygame.draw.line(screen, WHITE, (self.x * CELL_SIZE,self.y * CELL_SIZE -1), (round((self.health/self.health_max + self.x) * CELL_SIZE)-1,self.y * CELL_SIZE - 1), width=1)
        pygame.draw.rect(screen, BLACK, (self.x * CELL_SIZE,self.y * CELL_SIZE - 3, CELL_SIZE, 6 ),1)
        
        
        
# Test Hadriel:
class Canard(Unit):
    def __init__(self, x, y, health, attack_power, speed, team):
        super().__init__(x, y, health, attack_power, speed, team)
        self.image = "canard.png" if self.team == 'player' else "evil_canard.png"
        self.competences = competences.BouleDeFeu()
        
class Fee(Unit):
    def __init__(self, x, y, health, attack_power, speed, team):
        super().__init__(x, y, health, attack_power, speed, team)
        self.image = "fee.png" if self.team == 'player' else "evil_fee.png"
        self.competences = competences.Tir()
        
class guerrier(Unit):
    def __init__(self, x, y, health, attack_power, speed, team):
        super().__init__(x, y, health, attack_power, speed, team)
        self.competences = competences.Spin()
class archer(Unit):
    def __init__(self, x, y, health, attack_power, speed, team):
        super().__init__(x, y, health, attack_power, speed, team)
        self.competences = competences.Tir()

class mage(Unit):
    def __init__(self, x, y, health, attack_power, speed, team):
        super().__init__(x, y, health, attack_power, speed, team)
        self.competences = competences.BouleDeFeu()

class paladin(Unit):
    def __init__(self, x, y, health, attack_power, speed, team):
        super().__init__(x, y, health, attack_power, speed, team)
        self.competences = competences.Soin()
