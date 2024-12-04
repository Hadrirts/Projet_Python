import pygame
import random 
from abc import ABC, abstractmethod
from unit import *
"""
@author: Hadriel
"""

class Case(ABC):
    """
    x,y : coordonées du coin supérieur gauche de la case, int ou liste

    """
    
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
    color : tuple
        La couleur de la case
    __degats : int
        Les dégats infligés par la case
    __healing : int
        La guérison opérée par la case
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
        self.__Game = Game
           
    def draw(self, screen):
        #pygame.draw.rect(screen, self.color, self.rect)     # Case couleur unie
        screen.blit(self.image,(CELL_SIZE*self.x,CELL_SIZE*self.y))            # Case Image
    
    @abstractmethod
    def effect(self,unit):
        pass
    
    @property
    def Game(self):
        return self.__Game
            
class Lave(Case): 
    
    def __init__(self,x,y,Game):
        super().__init__(x,y,Game)
        #self.color = RED
        self.image = pygame.image.load("lave.jpg")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)) # redimensionner l'image
        self.__degats = 5
        
    @property
    def degats(self):
        return self.__degats
    
    def effect(self,unit):
        self.next = False # Rester sur l'unité
        if self.rect.collidepoint(unit.x * CELL_SIZE, unit.y * CELL_SIZE): # Si l'Unit est dans une zone de lave

            dx = random.choice([-1,0,1])   # Se déplace aléatoirement pour éviter la lave
            if dx == 0 :                      # Unit ne reste pas sur la case
               dy = random.choice([-1,1])
            else :
               dy = random.choice([-1,0,1])
                
            pygame.time.delay(100)
            unit.move(dx, dy)   # Déplacement
            self.Game.flip_display()
            unit.health -= self.__degats # Se brûle -> Perd 5 PV
            print(f"PV : {unit.health} (-{self.__degats})")
            print("-----------------------------")
            
            if  unit.health <= 0:                # Si l'unité a perdu tout ses PV
                self.Game.player_units.remove(unit)  # Retirer l'unité
                print("Dead")               
                self.Game.flip_display()
                self.next = True # Passer à l'unité suivante
                

class Guerison(Case):
    def __init__(self,x,y,Game):
        super().__init__(x,y,Game)
        #self.color = BEIGE
        self.image = pygame.image.load("healing.png")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)) # redimensionner l'image
        self.__healing = 5
        
    @property
    def healing(self):
        return self.__healing
    
    def effect(self,unit):
        self.next = False  # Pas de guérison -> rester sur l'unité
        if self.rect.collidepoint(unit.x * CELL_SIZE, unit.y * CELL_SIZE):  # Si Unit est dans une zone de guérison

            if unit.health + self.__healing > unit.health_max :
                unit.health = unit.health_max   # PV max
            else :
                unit.health += self.__healing   # Guérit -> Gagne PV
                
            print(f"PV : {unit.health} (+{self.__healing})")
            print("-----------------------------")
            
            self.Game.flip_display()
            self.next = True  # Guérison active -> passer à l'unité suivante
        

class Mur(Case):
    def __init__(self,x,y,Game):
        super().__init__(x,y,Game)
       # self.color = GREY
        self.image = pygame.image.load("mur.png")
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)) # redimensionner l'image
    
    def effect(self,unit,dx=0,dy=0): # *Décrire la methode plus haut*
        self.next = False
        if self.rect.collidepoint((unit.x + dx) * CELL_SIZE, (unit.y + dy) * CELL_SIZE):  # Si Unit est dans un mur
            return True

            

