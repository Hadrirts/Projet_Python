import pygame
import random

from unit import *
from cases import *
from interface import *

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
        self.player_units = [Canard(0, 0, 10, 2, 'player'),
                             Canard(1, 0, 10, 2, 'player')]

        self.enemy_units = [Canard(6, 6, 8, 1, 'enemy'),
                            Canard(7, 6, 8, 1, 'enemy')]
        # Coordonnées des cases spéciales
        lave_coord = [[2,2],[3,2],[2,1]]
        guerison_coord = [[5,6],[3,4]]
        mur_coord = [[2,4],[3,5],[4,4],[5,4],[6,3]]
        # On définit les cases
        lave = [Lave(i,j,self) for i,j, in lave_coord]
        guerison = [Guerison(i,j,self) for i,j in guerison_coord]
        mur = [Mur(i,j,self) for i,j in mur_coord]
        
        self.cases = lave+guerison+mur   # Cases spéciales *H*
       
        

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
                            for enemy in self.enemy_units:
                                if abs(selected_unit.x - enemy.x) <= 1 and abs(selected_unit.y - enemy.y) <= 1:
                                    selected_unit.attack(enemy)
                                    if enemy.health <= 0:
                                        self.enemy_units.remove(enemy)

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


    def flip_display(self):
        """Affiche le jeu."""

        # Affiche le background
        background = pygame.image.load("background.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        #self.screen.fill(BLACK)
        self.screen.blit(background,(0,0))
        # Affiche la grille
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

    # Créer une instance de l'interface
    interface = Interface()

    # Lancer le menu principal
    interface.display_menu()

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
