import math
from unit import *
import pygame
from abc import ABC, abstractmethod

GRID_SIZE = 13   # Nombre de cases
CELL_SIZE = 55   # Taille d'une case
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE


class Competence(ABC):
    def __init__(self, nom, degats, portee, cooldown):
        self.nom = nom
        self.degats = degats
        self.portee = portee
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.is_selected = False
        
    @abstractmethod
    def utiliser(self,caster):
        pass

    def is_available(self):
        return self.current_cooldown == 0

    def start_cooldown(self):
        self.current_cooldown = self.cooldown

    def decrement_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

class BouleDeFeu(Competence):
    def __init__(self):
        super().__init__(nom="Boule de feu", degats=10, portee=3, cooldown=3)
        self.zone_type = "cercle"
        self.rayon = 1
        self.image = pygame.image.load("feu.png")
        self.description = "Lance une boule de feu"

    def utiliser(self, caster, x, y, enemy_units):
        """Utilise la boule de feu, affectant une zone circulaire autour de la cible."""
        if abs(caster.x - x) <= self.portee and abs(caster.y - y) <= self.portee:
            affected_units = self.get_enemy_in_cercle(x, y, enemy_units)
            for unit in affected_units:
                unit.health -= (self.degats-unit.defense)
                if unit.health <= 0:
                    enemy_units.remove(unit)
            self.start_cooldown()

    def get_enemy_in_cercle(self, x, y, enemy_units):
        """Retourne les unités dans une zone circulaire autour de la cible."""
        affected_units = []
        for unit in enemy_units:
            distance = math.sqrt((unit.x - x)**2 + (unit.y - y)**2)
            if distance <= self.rayon:  # Vérifie si l'unité est dans la zone d'impact
                affected_units.append(unit)
        return affected_units
    
class Poing(Competence):
    def __init__(self,degats):
        super().__init__(nom="Coup de Poing", portee=1, cooldown=0,degats=degats)
        self.zone_type = "zone"
        self.image = pygame.image.load("poing.png")
        self.description = "Frappe les ennemis proches"

    def utiliser(self, caster, enemy_units):
        """Utilise le Coup de Poing pour infliger des dégâts dans un rayon autour du caster."""
        affected_units = self.get_enemy_in_cercle(caster, enemy_units)
        for unit in affected_units:
            unit.health -= (self.degats - unit.defense)
            if unit.health <= 0:
                enemy_units.remove(unit)
        self.start_cooldown()
        return f"utilise {self.nom} et touche {len(affected_units)} unités dans la zone circulaire."
    
    def get_enemy_in_cercle(self, caster, enemy_units):
        """Retourne les unités dans une zone circulaire autour de la cible."""
        affected_units = []
        for unit in enemy_units:
            distance = math.sqrt((unit.x - caster.x)**2 + (unit.y - caster.y)**2)
            if distance <= self.portee:  # Vérifie si l'unité est dans la zone d'impact
                affected_units.append(unit)
        return affected_units
    
    
class Tir(Competence):
    def __init__(self):
        super().__init__(nom="Tir", degats=10, portee=3, cooldown=3)
        self.zone_type = "ligne"
        self.image = pygame.image.load("arc.png")
        self.description = "Tire une flèche"
        
    def utiliser(self, caster, enemy_units, direction_active):
        """
        Utilise le tir en ligne, affectant une ligne droite dans la direction spécifiée.
        """
        affected_units = self.get_units_in_ligne(caster, enemy_units, direction_active)
        for unit in affected_units:
            unit.health -= (self.degats - unit.defense)
            if unit.health <= 0:
                enemy_units.remove(unit)
        self.start_cooldown()
        return f"utilise {self.nom} et touche {len(affected_units)} unités dans la direction {direction_active}."

    def get_units_in_ligne(self, caster, enemy_units, direction_active):
        """
        Retourne les unités dans une ligne droite dans la direction spécifiée.
        """
        affected_units = []
        dx, dy = 0, 0

        # Détermine le vecteur de direction
        if direction_active == "gauche":
            dx = -1
        elif direction_active == "droite":
            dx = 1
        elif direction_active == "haut":
            dy = -1
        elif direction_active == "bas":
            dy = 1

        # Parcourt les positions dans la direction active jusqu'à la portée maximale
        for step in range(1, self.portee + 1):
            ligne_x = caster.x + dx * step
            ligne_y = caster.y + dy * step

            # Vérifie que les coordonnées restent valides
            if 0 <= ligne_x < WIDTH // CELL_SIZE and 0 <= ligne_y < HEIGHT // CELL_SIZE:
                for unit in enemy_units:
                    if unit.x == ligne_x and unit.y == ligne_y:
                        affected_units.append(unit)

        return affected_units
    
class Soin(Competence):
    def __init__(self):
        super().__init__(nom="Soin", degats=-50, portee=1, cooldown=2)
        self.zone_type = "zone"
        self.image = pygame.image.load("soin.png")
        self.description = "Soigne les unités à proximité"

    def get_allies_in_cercle(self, caster, player_units):
        """Retourne les unités dans une zone circulaire autour du caster."""
        affected_units = []
        for unit in player_units:
            distance = math.sqrt((unit.x - caster.x)**2 + (unit.y - caster.y)**2)
            if distance <= self.portee:  # Vérifie si l'unité est dans la zone d'impact
                affected_units.append(unit)
        return affected_units
    
    def utiliser(self, caster, player_units):
        """Utilise le Soin pour soigner dans un rayon autour du caster."""
        affected_units = self.get_allies_in_cercle(caster, player_units)
        for unit in affected_units:
            unit.health = min(unit.health - self.degats, unit.health_max)
        self.start_cooldown()
        return f"utilise {self.nom} et touche {len(affected_units)} unités dans la zone."
    
class Spin(Competence):
    def __init__(self):
        super().__init__(nom="Spin", degats=20, portee=3, cooldown=2)
        self.zone_type = "zone"
        self.image = pygame.image.load("epee.png")
        self.description = "Attaque les ennemis autour"

    def utiliser(self, caster, enemy_units):
        """Utilise le Spin pour infliger des dégâts dans un rayon autour du caster."""
        affected_units = self.get_enemy_in_cercle(caster, enemy_units)
        for unit in affected_units:
            unit.health -= (self.degats - unit.defense)
            if unit.health <= 0:
                enemy_units.remove(unit)
        self.start_cooldown()
        return f"utilise {self.nom} et touche {len(affected_units)} unités dans la zone circulaire."
    
    def get_enemy_in_cercle(self, caster, enemy_units):
        """Retourne les unités dans une zone circulaire autour de la cible."""
        affected_units = []
        for unit in enemy_units:
            distance = math.sqrt((unit.x - caster.x)**2 + (unit.y - caster.y)**2)
            if distance <= self.portee:  # Vérifie si l'unité est dans la zone d'impact
                affected_units.append(unit)
        return affected_units
