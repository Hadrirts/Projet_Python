import pygame
import random
import numpy as np
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
        self.player_units = [] # à choisir dans l'interface

        self.enemy_units = [Fee(GRID_SIZE-1, GRID_SIZE-1, 8, 1, 5, 'enemy'),
                            Canard(GRID_SIZE-2, GRID_SIZE-1, 8, 1, 5, 'enemy')]
        
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
                        elif event.key == pygame.K_SPACE:  # Confirmer la visée
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
                        elif event.key == pygame.K_SPACE:  # Confirmer la visée
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
            # Dessine la zone circulaire de visée
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
            # Affiche la zone de visée valide
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

    def show_moveable_area(self, unit):
        """
        Dessine la zone atteignable calculée.
        """
        self.aim_surface.fill((0,0,0,0))

        for tile in unit.cases_acces:
            x, y = tile
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.aim_surface, (0, 255, 0, 100), rect)

    def handle_player_turn(self):
        """Tour du joueur"""
        for selected_unit in self.player_units:

            # Tant que l'unité n'a pas terminé son tour
            has_acted = False
            selected_unit.is_selected = True
            selected_unit.calcule_zone_mov()
            self.show_moveable_area(selected_unit)
            self.flip_display(moving=True)  # Met à jour l'écran de jeu
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
                            
                        selected_unit.move(dx, dy,self.mur) 
                        
                        self.flip_display(moving=True) # Met à jour l'écran de jeu
                        
                        
                        for case in self.cases:
                            if case.rect.collidepoint(selected_unit.x * CELL_SIZE, selected_unit.y * CELL_SIZE):  # Si l'unité est dans une case spéciale
                                case.effect(selected_unit,self.cases) # Applique les effets de la case

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
            enemy.move(dx, dy,self.mur)
            
            # Effets des cases
            for case in self.cases:
                if case.rect.collidepoint(enemy.x * CELL_SIZE, enemy.y * CELL_SIZE):  # Si l'unité est dans une case spéciale
                    case.effect(enemy,self.cases)   # Applique les effets de la case
                    break

            # Attaque si possible
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                enemy.attack(target)
                if target.health <= 0:
                    self.player_units.remove(target)
                    print("Team unit died :/")  



    def flip_display(self, viser_mode=False, moving=False):
        """Affiche le jeu."""

        # Affiche le background
        
        background = pygame.image.load("sol.png") 
        background = pygame.transform.scale(background, (WIDTH, HEIGHT)) 
        self.screen.blit(background,(0,0)) 
        
        for case in self.cases :
            case.draw(self.screen)       
        
        # Affiche les unités
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen)

        if(moving):
            self.screen.blit(self.aim_surface, (0, 0))

        if(viser_mode):
            # Affiche la surface de visée sur l'écran
            self.screen.blit(self.aim_surface, (0, 0))
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

    # Initialisation de Pygame
    pygame.init()
    
    pygame.mixer.init()

    # Jouer une musique de fond
    pygame.mixer.music.load("son_interface.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)  # Ajuster le volume

    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Monster Haven")

    # Instanciation du jeu
    game = Game(screen)

    # Créer une instance de l'interface
    interface = Interface()

    # Lancer le menu principal
    game.player_units = interface.display_menu()

    # Boucle principale du jeu
    while True:
        game.handle_player_turn()
        game.handle_enemy_turn()

if __name__ == "__main__":
    main()
