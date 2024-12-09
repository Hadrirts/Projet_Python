import pygame
import random
import numpy as np

from unit import *
from cases import *

# test for git

class Game:
    """
    Classe pour représenter le jeu.

    ...
    Attributs
    ---------
    screen: pygame.Surface
        La surface de la fenêtre du jeu.
    player_units : list[Unit]
        La liste des unités du joueur.
    enemy_units : list[Unit]
        La liste des unités de l'adversaire.
    """

    def __init__(self, screen):
        """
        Construit le jeu avec la surface de la fenêtre.

        Paramètres
        ----------
        screen : pygame.Surface
            La surface de la fenêtre du jeu.
        """
        self.screen = screen
        self.player_units = [archer(0, 0, 10, 2, 'player'),
                             mage(1, 0, 10, 2, 'player')]

        self.enemy_units = [Unit(6, 6, 8, 1, 'enemy'),
                            Unit(7, 6, 8, 1, 'enemy')]
        
        self.cases = [Lave(2,2,self),
                      Guerison(5,6,self),
                      Mur(3,4,self)] # Cases spéciales *H*
        self.aim_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    def use_skillshot(self, unit, competence):
        x, y = unit.x, unit.y
        viser = True
        direction_active = None

        while viser:
            self.afficher_zone_visee(unit, x, y, competence, direction_active)
            self.flip_display(viser_mode=True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if competence.zone_type == "cercle":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT and np.sqrt((x - unit.x - 1)**2 + (y - unit.y)**2) <= competence.portee:
                            x = max(0, x - 1)
                        elif event.key == pygame.K_RIGHT and np.sqrt((x - unit.x + 1)**2 + (y - unit.y)**2) <= competence.portee:
                            x = min(WIDTH // CELL_SIZE - 1, x + 1)
                        elif event.key == pygame.K_UP and np.sqrt((x - unit.x)**2 + (y - unit.y - 1)**2) <= competence.portee:
                            y = max(0, y - 1)
                        elif event.key == pygame.K_DOWN and np.sqrt((x - unit.x)**2 + (y - unit.y + 1)**2) <= competence.portee:
                            y = min(HEIGHT // CELL_SIZE - 1, y + 1)
                    elif event.key == pygame.K_RETURN:  # Confirmer la visée
                        competence.utiliser(unit,x,y, self.enemy_units)
                        viser = False
                    elif event.key == pygame.K_ESCAPE:  # Annuler
                        viser = False
                elif competence.zone_type == "ligne":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            direction_active = "gauche"
                        elif event.key == pygame.K_RIGHT:
                            direction_active = "droite"
                        elif event.key == pygame.K_UP:
                            direction_active = "haut"
                        elif event.key == pygame.K_DOWN:
                            direction_active = "bas"
                    elif event.key == pygame.K_RETURN:  # Confirmer la visée
                        competence.utiliser(unit, self.enemy_units,direction_active)
                        viser = False
                    elif event.key == pygame.K_ESCAPE:  # Annuler
                        viser = False

    def afficher_zone_visee(self,unit, target_x, target_y, competence, direction_active = None):
        self.aim_surface.fill((0, 0, 0, 0))
        if competence.zone_type == "cercle":
            rayon = competence.rayon
            # Affiche la zone de déplacement valide
            for x in range(-competence.portee, competence.portee + 1):
                for y in range(-competence.portee, competence.portee + 1):
                    distance = np.sqrt(x**2 + y**2)
                    if distance <= competence.portee:
                        case_x = unit.x + x
                        case_y = unit.y + y
                        if 0 <= case_x < WIDTH // CELL_SIZE and 0 <= case_y < HEIGHT // CELL_SIZE:
                            rect = pygame.Rect(case_x * CELL_SIZE, case_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                            pygame.draw.rect(self.aim_surface, (128, 128, 128, 100), rect)
            # Dessine la zone circulaire de visée en rouge
            for x in range(-rayon, rayon + 1):
                for y in range(-rayon, rayon + 1):
                    distance = np.sqrt(x**2 + y**2)
                    if distance <= rayon:
                        case_x = target_x + x
                        case_y = target_y + y
                        if 0 <= case_x < WIDTH // CELL_SIZE and 0 <= case_y < HEIGHT // CELL_SIZE:
                            rect = pygame.Rect(case_x * CELL_SIZE, case_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                            pygame.draw.rect(self.aim_surface, (255, 0, 0, 200), rect)

        elif competence.zone_type == "ligne":
            # Affiche la zone de déplacement valide
            directions = {"droite": (1, 0),
                          "gauche": (-1, 0),
                          "bas": (0, 1),
                          "haut": (0, -1),
                          }  # Droite, Gauche, Bas, Haut
            for direction, (dx, dy) in directions.items():
                for step in range(1, competence.portee + 1):  # Jusqu'à la portée maximale
                    case_x = unit.x + dx * step
                    case_y = unit.y + dy * step
                    if 0 <= case_x < WIDTH // CELL_SIZE and 0 <= case_y < HEIGHT // CELL_SIZE:
                        rect = pygame.Rect(case_x * CELL_SIZE, case_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        if direction == direction_active:
                            pygame.draw.rect(self.aim_surface, (255, 0, 0, 200), rect)  # Rouge pour la direction active
                        else:
                            pygame.draw.rect(self.aim_surface, (255, 255, 0, 100), rect)  # Jaune pour les autres         

        # Affiche la surface de visée sur l'écran
        self.screen.blit(self.aim_surface, (0, 0))

    def handle_player_turn(self):
        """Tour du joueur"""
        for selected_unit in self.player_units:

            # Tant que l'unité n'a pas terminé son tour
            has_acted = False
            selected_unit.is_selected = True
            self.flip_display()
            while not has_acted:

                # Important: cette boucle permet de gérer les événements Pygame
                for event in pygame.event.get():

                    # Gestion de la fermeture de la fenêtre
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    # Gestion des touches du clavier
                    if event.type == pygame.KEYDOWN:

                        # Déplacement (touches fléchées)
                        dx, dy = 0, 0
                        if event.key == pygame.K_LEFT:
                            dx = -1
                        elif event.key == pygame.K_RIGHT:
                            dx = 1
                        elif event.key == pygame.K_UP:
                            dy = -1
                        elif event.key == pygame.K_DOWN:
                            dy = 1
                            
                    # Gestion des déplacements 
                        mur = False
                        for case in self.cases:
                            if isinstance(case,Mur):                       # Gestion des murs
                                if case.effect(selected_unit,dx,dy):   # Si l'unité rencontre un mur
                                    mur = True
                                    break
                        if mur == False:
                            selected_unit.move(dx, dy)         
                                                
                        self.flip_display() # Met à jour l'écran de jeu
                                                
                        for case in self.cases:
                            if case.rect.collidepoint(selected_unit.x * CELL_SIZE, selected_unit.y * CELL_SIZE):  # Si l'unité est dans une case spéciale
                                case.effect(selected_unit)   # Applique les effets de la case
                                has_acted = case.next        
                                selected_unit.is_selected = not(case.next)
                                break
                        
                        # Attaque (touche espace) met fin au tour
                        if event.key == pygame.K_SPACE:
                            #utilisation de la compétence
                            competence = selected_unit.competences
                            if competence.type_competence == "skillshot":
                                self.use_skillshot(selected_unit, competence)
                            has_acted = True
                            selected_unit.is_selected = False

    def handle_enemy_turn(self):
        """IA très simple pour les ennemis."""
        for enemy in self.enemy_units:

            # Déplacement aléatoire
            target = random.choice(self.player_units)
            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
            enemy.move(dx, dy)

            # Attaque si possible
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                enemy.attack(target)
                if target.health <= 0:
                    self.player_units.remove(target)

    def flip_display(self, viser_mode=False):
        """Affiche le jeu avec ou sans mode visée."""
        self.screen.fill(BLACK)

        # Affiche la grille
        for x in range(0, WIDTH, CELL_SIZE):
            for y in range(0, HEIGHT, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

        # Affiche les cases spéciales
        for case in self.cases:
            case.draw(self.screen)

        # Affiche les unités
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen)

        # Ajoute la surface de visée si en mode visée
        if viser_mode:
            
            self.screen.blit(self.aim_surface, (0, 0))
            

        # Rafraîchit l'écran
        pygame.display.flip()

      


def main():

    # Initialisation de Pygame
    pygame.init()

    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon jeu de stratégie")

    # Instanciation du jeu
    game = Game(screen)

    # Boucle principale du jeu
    while True:
        game.handle_player_turn()
        game.handle_enemy_turn()


if __name__ == "__main__":
    main()

