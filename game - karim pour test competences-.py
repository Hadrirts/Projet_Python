import pygame
import random

from unit import *
from cases import * # *H*

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
        self.player_units = [mage(0, 0, 10, 2, 'player'),
                             mage(1, 0, 10, 2, 'player')]

        self.enemy_units = [Unit(6, 6, 8, 1, 'enemy'),
                            Unit(7, 6, 8, 1, 'enemy')]
        
        self.cases = [Lave(2,2,self),
                      Guerison(5,6,self),
                      Mur(3,4,self)] # Cases spéciales *H*

    def viser_et_utiliser_competence(self, unit, competence):
        """Permet de viser une zone et d'utiliser une compétence."""
        x, y = unit.x, unit.y  # Point de départ (position de l'unité)
        rayon = competence.rayon  # Rayon d'effet de la compétence
        viser = True

        while viser:
            self.flip_display()
            self.afficher_zone_visee(self.screen, x, y, rayon)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN:
                    # Déplacement du curseur de visée
                    if event.key == pygame.K_LEFT:
                        x = max(0, x - 1)
                    elif event.key == pygame.K_RIGHT:
                        x = min(WIDTH // CELL_SIZE - 1, x + 1)
                    elif event.key == pygame.K_UP:
                        y = max(0, y - 1)
                    elif event.key == pygame.K_DOWN:
                        y = min(HEIGHT // CELL_SIZE - 1, y + 1)

                    # Validation de la visée
                    elif event.key == pygame.K_RETURN:
                        competence.utiliser(unit, x, y, self.enemy_units)
                        viser = False

                    # Annuler la visée
                    elif event.key == pygame.K_ESCAPE:
                        viser = False


    def afficher_zone_visee(self, screen, x, y, rayon, couleur=(255, 0, 0, 128)):
        """Affiche la zone de visée pour un skillshot."""
        for dx in range(-rayon, rayon + 1):
            for dy in range(-rayon, rayon + 1):
                if abs(dx) + abs(dy) <= rayon:  # Limite la portée à un rayon Manhattan
                    rect = pygame.Rect(
                        (x + dx) * CELL_SIZE, (y + dy) * CELL_SIZE, CELL_SIZE, CELL_SIZE
                    )
                    pygame.draw.rect(screen, couleur, rect, 0)

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
                        
                        for case in self.cases:
                            if isinstance(case,Mur):                       # Gestion des murs
                                case.dx = dx
                                case.dy = dy
                                if not(case.effect(selected_unit)):    # Gestion des murs
                                    selected_unit.move(dx, dy)         
                        
                        self.flip_display() # Met à jour l'écran de jeu
                        
                        # Effets des cases *H*  -->
                        
                        for case in self.cases:
                            if case.rect.collidepoint(selected_unit.x * CELL_SIZE, selected_unit.y * CELL_SIZE):  # Si l'unité est dans une case spéciale
                                case.effect(selected_unit)   # Applique les effets de la case
                                has_acted = case.next        
                                selected_unit.is_selected = not(case.next)
                                break
                                
                        # <-- *H*
                        
                        # Attaque (touche espace) met fin au tour
                        if event.key == pygame.K_SPACE:
                            #utilisation de la compétence
                            competence = selected_unit.competences
                            print(competence)
                            if competence.type_competence == "skillshot":
                                self.viser_et_utiliser_competence(selected_unit, competence)
                                print("Skillshot")
                            else:
                                print("Attaque")
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


    def flip_display(self, viser=False):
        """Affiche le jeu."""

        # Affiche la grille
        if not viser:
            self.screen.fill(BLACK)  # Nettoie l'écran uniquement en mode normal.
        for x in range(0, WIDTH, CELL_SIZE):
            for y in range(0, HEIGHT, CELL_SIZE):
                self.rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, WHITE, self.rect, 1)
                
        # Affiche les cases spéciales *H* -->
        
        for case in self.cases :
            case.draw(self.screen)
            
        # <-- *H*
        
        # Affiche les unités
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen)

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

