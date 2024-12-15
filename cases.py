import pygame
import random 
from abc import ABC, abstractmethod
from unit import *
from competences import *

# Générer des cases aléatoirement
def rand_coord(grid_size,nb_cases,coord_list):
    
    """
    Fonction qui permet de générer des coordonnées aléatoires de cases non occupées
    
    -----
    INPUT :
        grid_size : int
            Taille de la fenêtre de jeu (nombre de cases)
        nb_cases : int
            Nombre de coordonnées de cases à générer
        coord_list : list[list[int][2]]
            Liste des coordonnées des cases déjà occupées
    OUTPUT:
        coord : list[list[int][2]]
            Liste de coordonnées de cases libres générées
    """
    coord = []  
    min_val = 0
    max_val = grid_size-1
    for i in range(nb_cases):
        while True:
            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)
            couple = [a,b]
            
            if couple not in coord_list:
                coord.append(couple)
                coord_list.append(couple)
                break

    return coord
    
class Case(ABC):

    """
    Classe pour représenter une case spéciale.

    ...
    Attributs
    ---------
    x : int
        La position x du coin supérieur gauche de la case.
    y : int
        La position y du coin supérieur gauche de la case.
    rect : pygame.Rect
        La définition de la case sur la grille
    degats : int
        Les dégats infligés par la case Lave
    healing : int
        La guérison opérée par la case Guerison
    Game : Game
    image : pygame.surface.Surface
        Image de la case
    next : Indique que l'unité finit son tour

    Méthodes
    --------
    draw(dx, dy)
        Dessine la case sur la grille
    effect(unit)
        Applique les effets de la case sur l'unité

    """

    
    def __init__(self,x,y,Game):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(CELL_SIZE*self.x,CELL_SIZE*self.y,CELL_SIZE,CELL_SIZE)
        self.Game = Game
           
    def draw(self, screen):
        screen.blit(self.image,(CELL_SIZE*self.x,CELL_SIZE*self.y))            # Case Image
    
    @abstractmethod
    def effect(self,unit):
        pass
            
class Lave(Case): 
    
    def __init__(self,x,y,Game):
        super().__init__(x,y,Game)
        self.image = pygame.image.load('lave.png')
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.degats = 5
    
    def effect(self,unit,cases):
        self.next = False # Rester sur l'unité
        if self.rect.collidepoint(unit.x * CELL_SIZE, unit.y * CELL_SIZE): # Si l'Unit est dans une zone de lave
            while True :
                dx = random.choice([-1,0,1])   # Se déplace aléatoirement pour éviter la lave
                if dx == 0 :                      # Unit ne reste pas sur la case
                   dy = random.choice([-1,1])
                else :
                   dy = random.choice([-1,0,1])
                safe = True
                for case in cases:
                    # Eviter que l'unité aterrisse dans une autre case spéciale ou en dehors de sa zone de mouvement
                    if (case.rect.collidepoint((unit.x+dx) * CELL_SIZE, (unit.y+dy) * CELL_SIZE) or 
                    not(0 <= unit.x + dx < GRID_SIZE) or not(0 <= unit.y + dy < GRID_SIZE) or
                    ((unit.x+dx,unit.y+dy) not in unit.cases_acces)): 
                        safe = False
                        break  # Sortir de la boucle for et chercher une autre case

                if safe == True: # Si la case est libre
                    break  # Sortir de la boucle while pour faire bouger l'unité
                
            
            pygame.time.delay(100)
            murs = []
            for case in cases :
                if isinstance(case,Mur):
                    murs.append(case)
            unit.move(dx, dy, murs)   # Déplacement
            unit.health -= self.degats # Se brûle -> Perd 5 PV
            print(unit.team+" unit in lava")
            self.Game.flip_display(moving=True)
            
            if  unit.health <= 0:                # Si l'unité a perdu tout ses PV
                self.Game.player_units.remove(unit)  # Retirer l'unité
                if unit.team == "player":
                    print("Team unit died :/")  
                elif unit.team == "enemy":
                    print("Enemy unit died ;)")
                self.next = True # Passer à l'unité suivante
                
            self.Game.flip_display(moving=True)
                
class Guerison(Case):
    def __init__(self,x,y,Game):
        super().__init__(x,y,Game)
        self.image = pygame.image.load('coeur.png')
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        #self.healing = 5
    
    def effect(self,unit,cases):
        self.next = False  # Ne pas passer à l'unité suivante
        if self.rect.collidepoint(unit.x * CELL_SIZE, unit.y * CELL_SIZE):  # Si Unit est dans une zone de guérison

            # if unit.health + self.__healing > unit.health_max :
            unit.health = unit.health_max   # PV max
            # else :
            #     unit.health += self.__healing   # Guérit -> Gagne PV
                
            print(unit.team+" unit healed")
            
            cases.remove(self) # faire disparaître la case
            self.Game.flip_display()

class Mur(Case):
    def __init__(self,x,y,Game):
        super().__init__(x,y,Game)
        self.image = pygame.image.load('mur.png')
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
    
    def effect(self,unit,dx=0,dy=0):
        self.next = False
        if self.rect.collidepoint((unit.x + dx) * CELL_SIZE, (unit.y + dy) * CELL_SIZE):  # Si Unit est dans un mur
            return True

# Objets pouvant être ramassés par l'unité

class Objet(Case):
    def effect(self,unit,cases):
        self.next = False  # Ne pas passer à l'unité suivante
        if self.rect.collidepoint(unit.x * CELL_SIZE, unit.y * CELL_SIZE): # Si l'unité est dans la case de l'objet
            for u in unit.competences : # On vérifie que l'unité ne possède pas déjà la compétence
                if type(self.competence) == type(u):
                    return
            unit.competences.append(self.competence) # Ajouter la compétence de l'objet à l'unité
            cases.remove(self) # Retirer l'objet
            
class Feu(Objet):
    def __init__(self,x,y,Game):
        super().__init__(x,y,Game)
        self.competence = BouleDeFeu()
        self.image = pygame.transform.scale(self.competence.image, (CELL_SIZE, CELL_SIZE))

class Med(Objet):
    def __init__(self,x,y,Game):
        super().__init__(x,y,Game)
        self.competence = Soin()
        self.image = pygame.transform.scale(self.competence.image, (CELL_SIZE, CELL_SIZE))
        
class Epee(Objet):
    def __init__(self,x,y,Game):
        super().__init__(x,y,Game)
        self.competence = Spin()
        self.image = pygame.transform.scale(self.competence.image, (CELL_SIZE, CELL_SIZE))
        
class Arc(Objet):
    def __init__(self,x,y,Game):
        super().__init__(x,y,Game)
        self.competence = Tir()
        self.image = pygame.transform.scale(self.competence.image, (CELL_SIZE, CELL_SIZE))


            

