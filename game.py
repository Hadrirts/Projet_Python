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
                             Fee(1, 0, 10, 2, 'player')]

        self.enemy_units = [Fee(GRID_SIZE-1, GRID_SIZE-1, 8, 1, 'enemy'),
                            Canard(GRID_SIZE-2, GRID_SIZE-1, 8, 1, 'enemy')]
        
        # Coordonnées des cases spéciales
        lave_coord = []
        guerison_coord = [[6,6],[3,3],[9,3],[3,9],[9,9]]
        mur_coord = [[2,2],[2,3],[3,2],[9,2],[10,2],[10,3],[2,9],[2,10],[3,10],[10,9],[10,10],[9,10],
                     [5,4],[6,4],[7,4],[5,8],[6,8],[7,8],
                     [0,6],[12,6],[6,1],[6,11]]   
        # Générer des cases de lave aléatoirement
        list_coord = mur_coord+guerison_coord+[[i.x,i.y] for i in self.player_units+self.enemy_units] # Liste des cases déjà prises
        lave_coord = rand_coord(GRID_SIZE,10,list_coord)
        
        # On définit les cases
        lave = [Lave(i,j,self) for i,j, in lave_coord]
        guerison = [Guerison(i,j,self) for i,j in guerison_coord]
        self.mur = [Mur(i,j,self) for i,j in mur_coord]
        
        self.cases = lave+self.mur+guerison
       
        

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
                        # mur = False
                        # for case in self.cases:
                        #     if isinstance(case,Mur):                       # Gestion des murs
                        #         if case.effect(selected_unit,dx,dy):   # Si l'unité rencontre un mur
                        #             mur = True
                        #             break
                        # if mur == False:
                        #     selected_unit.move(dx, dy) 
                        selected_unit.move(dx, dy,self.mur) 
                        
                        self.flip_display() # Met à jour l'écran de jeu
                        
                        # Effets des cases *H*  -->
                        
                        for case in self.cases:
                            if case.rect.collidepoint(selected_unit.x * CELL_SIZE, selected_unit.y * CELL_SIZE):  # Si l'unité est dans une case spéciale
                                case.effect(selected_unit,self.cases) # Applique les effets de la case

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
                                        print("Enemy unit died ;)")

                            has_acted = True
                            selected_unit.is_selected = False

    def handle_enemy_turn(self):
        """IA très simple pour les ennemis."""
        for enemy in self.enemy_units:

            # Déplacement aléatoire
            target = random.choice(self.player_units)
            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
            enemy.move(dx, dy,self.mur)
            
            # Effets des cases
            for case in self.cases:
                if case.rect.collidepoint(enemy.x * CELL_SIZE, enemy.y * CELL_SIZE):  # Si l'unité est dans une case spéciale
                    case.effect(enemy)   # Applique les effets de la case
                    break

            # Attaque si possible
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                enemy.attack(target)
                if target.health <= 0:
                    self.player_units.remove(target)
                    print("Team unit died :/")  



    def flip_display(self):
        """Affiche le jeu."""

        # Affiche le background
        
        background = pygame.image.load("sol.png") 
        background = pygame.transform.scale(background, (WIDTH, HEIGHT)) 
        self.screen.blit(background,(0,0)) 

        # # Affiche la grille
        # for x in range(0, WIDTH, CELL_SIZE):
        #     for y in range(0, HEIGHT, CELL_SIZE):
        #         self.rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        #         pygame.draw.rect(self.screen, WHITE, self.rect, 1)
                
        # Affiche les cases spéciales
        
        for case in self.cases :
            case.draw(self.screen)       
        
        # Affiche les unités
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen)
        
        # Rafraîchit l'écran
        pygame.display.flip()
        if not(self.enemy_units) :
            print("All enemy units died!")
            self.display_end_message("You won!")
            
        if not(self.player_units) :
            print("All team units died :(")
            self.display_end_message("Game Over")

    def display_end_message(self, message):
        """Affiche un message de fin, uniquement 'You won' ou 'Game Over'"""
        #self.screen.fill(BLACK)  
    
        # Afficher le message au centre de l'écran
        font = pygame.font.Font(None, 72)
        text_surface = font.render(message, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)
    
        pygame.display.flip()
    
        # Attendre un moment pour laisser le joueur lire le message
        pygame.time.wait(3000)
    
        # Quitter le jeu après le message
        pygame.quit()
        sys.exit()

    def display_end_message(self, message):
        """Affiche un message de fin, uniquement 'You won' ou 'Game Over'"""
        #self.screen.fill(BLACK)  

        # Afficher le message au centre de l'écran
        font = pygame.font.Font(None, 72)
        text_surface = font.render(message, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)

        pygame.display.flip()

        # Attendre un moment pour laisser le joueur lire le message
        pygame.time.wait(3000)

        # Quitter le jeu après le message
        pygame.quit()

        sys.exit()

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
