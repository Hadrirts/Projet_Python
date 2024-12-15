import pygame
from competences import *
import heapq

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
D_GREY = (130,130,130)



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
    health_max : int                  
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

    def __init__(self, x, y, health, attack_power, defense, speed, team):
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
        self.defense = defense
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
        self.pos_debut_tour = (self.x, self.y)  # Mettre à jour la position de début de tour

    def attack(self, target):
        """Attaque une unité cible."""
        if abs(self.x - target.x) <= 1 and abs(self.y - target.y) <= 1:
            target.health -= (self.attack_power-target.defense)

    def draw(self, screen):
        """Affiche l'unité sur l'écran."""
        
        if self.is_selected:
            pygame.draw.circle(screen, GREEN, (self.x * CELL_SIZE + CELL_SIZE //
                                2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
            
        screen.blit(self.image,(self.x * CELL_SIZE,self.y * CELL_SIZE)) # afficher l'image
        
        # Barre de santé
        pygame.draw.rect(screen, PURPLE, (self.x * CELL_SIZE,self.y * CELL_SIZE - 3, round(CELL_SIZE * self.health/self.health_max), 6 ))
        pygame.draw.line(screen, WHITE, (self.x * CELL_SIZE,self.y * CELL_SIZE -1), (round((self.health/self.health_max + self.x) * CELL_SIZE)-1,self.y * CELL_SIZE - 1), width=1)
        pygame.draw.rect(screen, BLACK, (self.x * CELL_SIZE,self.y * CELL_SIZE - 3, CELL_SIZE, 6 ),1)
        
        # Affichage des compétences
        for i,c in zip(range(len(self.competences)),self.competences):
            taille = CELL_SIZE//3
            pos_x = CELL_SIZE*self.x + i*taille
            pos_y = CELL_SIZE*(self.y+1) 
            if c.is_selected and self.is_selected :  
                color = D_GREY if c.current_cooldown > 0 else GREEN
                pygame.draw.circle(screen, color, (pos_x + taille // 2, pos_y + taille // 2), CELL_SIZE // 6)
            picture = pygame.transform.scale(c.image, (taille, taille)) # redimensionner l'image
            screen.blit(picture,(pos_x,pos_y))   

class Guerrier(Unit):
    def __init__(self, x=0, y=0, health=100, attack_power=20, defense=10, speed=5, team='player'):
        super().__init__(x, y, health, attack_power, defense, speed, team)
        picture = "guerrier.png"
        self.image = pygame.image.load(picture)
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)) 
        self.competences = [Spin()]
        
class Archer(Unit):
    def __init__(self, x=0, y=0, health=80, attack_power=15, defense=5, speed=6, team='player'):
        super().__init__(x, y, health, attack_power, defense, speed, team)
        picture = "archer.png"
        self.image = pygame.image.load(picture)
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)) 
        self.competences = [Tir()]

class Mage(Unit):
    def __init__(self, x=0, y=0, health=60, attack_power=25, defense=3, speed=6, team='player'):
        super().__init__(x, y, health, attack_power, defense, speed, team)
        picture = "mage.png"
        self.image = pygame.image.load(picture)
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)) 
        self.competences = [BouleDeFeu()]

class Paladin(Unit):
    def __init__(self, x=0, y=0, health=120, attack_power=18, defense=15, speed=4, team='player'):
        super().__init__(x, y, health, attack_power, defense, speed, team)
        picture = "paladin.png"
        self.image = pygame.image.load(picture)
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)) # redimensionner l'image
        self.competences = [Soin()]

class Monstre(Unit):
    def __init__(self, x=0, y=0, health=150, attack_power=30, defense=8, speed=10, monstre="monstre 1", team='enemy'):
        super().__init__(x, y, health, attack_power, defense, speed, team)
        if monstre == "monstre 1":
            picture = "monstre1.png"
        if monstre == "monstre 2":
            picture = "monstre2.png"
        if monstre == "monstre 3":
            picture = "monstre3.png"
        self.image = pygame.image.load(picture)
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)) # redimensionner l'image
        self.competences = [Tir()]
        
import heapq

def astar(start, goal, grid, walls):
    def heuristic(a, b):
        # Heuristique de Manhattan pour estimer la distance entre deux points
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    # Ajouter le point de départ à la file de priorité avec un coût initial de 0
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        # Extraire le nœud avec le coût estimé le plus bas
        _, current = heapq.heappop(open_set)

        if current == goal:
            # Si nous avons atteint le but, reconstruire le chemin
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            tentative_g_score = g_score[current] + 1

            if 0 <= neighbor[0] < len(grid) and 0 <= neighbor[1] < len(grid[0]) and neighbor not in walls:
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    # Ajouter le voisin à la file de priorité
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []
        