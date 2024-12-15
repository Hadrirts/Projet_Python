import pygame
import random
import numpy as np
from unit import *
from cases import *
from interface import *
from competences import *




import heapq

def astar(start, goal, grid_size, walls):
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

            if 0 <= neighbor[0] < grid_size and 0 <= neighbor[1] < grid_size and neighbor not in walls:
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    # Ajouter le voisin à la file de priorité
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []

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

        self.enemy_units = [
            Monstre(GRID_SIZE-1, GRID_SIZE-1, health=30, attack_power=30, defense=8, speed=2, monstre="monstre 1", team='enemy'),
            Monstre(GRID_SIZE-2, GRID_SIZE-1, health=30, attack_power=30, defense=8, speed=2, monstre="monstre 1", team='enemy'),
            Monstre(GRID_SIZE-3, GRID_SIZE-1, health=30, attack_power=30, defense=8, speed=2, monstre="monstre 1", team='enemy')
        ]
        
        # Coordonnées des cases spéciales et objets

        lave_coord = []
        guerison_coord = [[6,6],[3,3],[9,3],[3,9],[9,9]]
        mur_coord = [[2,2],[2,3],[3,2],[9,2],[10,2],[10,3],[2,9],[2,10],[3,10],[10,9],[10,10],[9,10],
                     [5,4],[6,4],[7,4],[5,8],[6,8],[7,8],
                     [0,6],[12,6],[6,1],[6,11]]   
        objet_coord = [[11,1],[1,11],[6,3],[6,9]]
        # Générer des cases de lave aléatoirement
        list_coord = mur_coord+guerison_coord+objet_coord+[[i.x,i.y] for i in self.player_units+self.enemy_units] # Liste des cases déjà prises
        lave_coord = rand_coord(GRID_SIZE,10,list_coord)
        
        # On définit les cases
        lave = [Lave(i,j,self) for i,j, in lave_coord]
        guerison = [Guerison(i,j,self) for i,j in guerison_coord]
        self.mur = [Mur(i,j,self) for i,j in mur_coord]
        objets = [Feu(11,1,self),Arc(1,11,self),Med(6,3,self),Epee(6,9,self)]
        
        # objet_coord = 
        
        self.cases = lave+self.mur+guerison+objets

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
                        elif event.key == pygame.K_RETURN:  # Annuler
                            viser = False
                elif competence.zone_type == "zone":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:  # Confirmer la visée
                            if competence.nom == "Soin":
                                competence.utiliser(unit, self.player_units)
                            else:
                                competence.utiliser(unit, self.enemy_units)
                            viser = False
                        elif event.key == pygame.K_RETURN:  # Annuler
                            viser = False
                        

    def afficher_zone_visee(self,unit, target_x, target_y, competence, direction_active = None):
        self.aim_surface.fill((0, 0, 0, 0))
        if competence.zone_type != "ligne":
            # Affiche la zone valide
            for x in range(-competence.portee, competence.portee + 1):
                for y in range(-competence.portee, competence.portee + 1):
                    distance = np.sqrt(x**2 + y**2)
                    if distance <= competence.portee:
                        case_x = unit.x + x
                        case_y = unit.y + y
                        if 0 <= case_x < WIDTH // CELL_SIZE and 0 <= case_y < HEIGHT // CELL_SIZE:
                            rect = pygame.Rect(case_x * CELL_SIZE, case_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                            pygame.draw.rect(self.aim_surface, (128, 128, 128, 100), rect)
            if competence.zone_type == "cercle":
                rayon = competence.rayon
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
        else:
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
                            pygame.draw.rect(self.aim_surface, (128, 128, 128, 100), rect)  # Jaune pour les autres    
            

    def show_moveable_area(self, unit):
        """
        Dessine la zone atteignable calculée.
        """
        self.aim_surface.fill((0,0,0,0))

        for tile in unit.cases_acces:
            x, y = tile
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.aim_surface, (0, 255, 0, 30), rect)

    def handle_player_turn(self):
        """Tour du joueur"""
        for selected_unit in self.player_units:

            # Tant que l'unité n'a pas terminé son tour
            has_acted = False
            selected_unit.is_selected = True
            selected_unit.calcule_zone_mov()
            self.show_moveable_area(selected_unit)
            self.flip_display(moving=True)  # Met à jour l'écran de jeu
            competence = None
            sel = 0 # Séléction de la compétence
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
                        
                        # Gestion des effets des cases spéciales
                        for case in self.cases:
                            if case.rect.collidepoint(selected_unit.x * CELL_SIZE, selected_unit.y * CELL_SIZE):  # Si l'unité est dans une case spéciale
                                case.effect(selected_unit,self.cases) # Applique les effets de la case

                                has_acted = case.next        
                                selected_unit.is_selected = not(case.next)
                                break
                                                        
                        # Gère la séléction de la compétence à utliser
                        if (event.key in (pygame.K_1, pygame.K_KP1)) or (len(selected_unit.competences) == 1):
                            competence = selected_unit.competences[0]
                            sel = 0
                        elif (event.key in (pygame.K_2, pygame.K_KP2)) and (len(selected_unit.competences) >= 2):
                            competence = selected_unit.competences[1]
                            sel = 1
                        elif (event.key in (pygame.K_3, pygame.K_KP3)) and (len(selected_unit.competences) >= 3):
                            competence = selected_unit.competences[2]
                            sel = 2
                        elif (event.key in (pygame.K_4 , pygame.K_KP4)) and (len(selected_unit.competences) >= 4):
                            competence = selected_unit.competences[3]
                            sel = 3
                        elif not(competence):
                            competence = selected_unit.competences[0]
                            sel = 0
                            
                        for comp in selected_unit.competences:
                            comp.is_selected = False    
                            
                        selected_unit.competences[sel].is_selected = True
                        self.flip_display(moving=True)
                            
                        # Attaque (touche espace) met fin au tour  
                        if event.key == pygame.K_SPACE:
                            # Vérifier si la compétence est disponible
                            if competence.is_available():
                                # Utilisation de la compétence
                                self.use_skillshot(selected_unit, competence)
                                has_acted = True
                                selected_unit.is_selected = False
                        # Fin du tour sans utiliser de compétence (touche return)
                        elif event.key == pygame.K_RETURN:
                            has_acted = True
                            selected_unit.is_selected = False
            # Décrémenter les cooldowns des compétences de l'unité
            for comp in selected_unit.competences:
                comp.decrement_cooldown()

    def handle_enemy_turn(self):
        """IA améliorée pour les ennemis."""
        for enemy in self.enemy_units:
            if not self.player_units:
                self.flip_display()
            # 1. Prioriser la cible (par exemple, cible la plus faible en points de vie)
            target = min(self.player_units, key=lambda unit: unit.health)

            # 2. Calculer le chemin le plus court vers la cible
            start = (enemy.x, enemy.y)
            goal = (target.x, target.y)
            walls = {(mur.x, mur.y) for mur in self.mur}
            grid_size = GRID_SIZE
            path = astar(start, goal, grid_size, walls)
            enemy.calcule_zone_mov()

            if path:
                # Trouver la case accessible la plus proche de l'objectif
                for step in path:
                    if step in enemy.cases_acces:
                        dx = step[0] - enemy.x
                        dy = step[1] - enemy.y
                        enemy.move(dx, dy, self.mur)
                        self.flip_display()
                        pygame.time.wait(200)


            # 4. Utiliser une compétence ou attaquer
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                # Si l'ennemi a une compétence, l'utiliser
                if hasattr(enemy, 'competence'):
                    enemy.competence.use(target)
                    print(f"utilise {enemy.competence.nom}!")
                else:
                    # Sinon, attaque classique
                    enemy.attack(target)
                    print(f"attaque!")

                # Supprime l'unité cible si elle est morte
                if target.health <= 0:
                    self.player_units.remove(target)
                    print("a été éliminé !")
                    
    # Affiche les instructions :          
    def afficher_instructions(self, unit, viser_mode=False, moving=False):
        fond = pygame.Rect(0,HEIGHT,WIDTH,50)       # Fond noir
        pygame.draw.rect(self.screen,BLACK,fond)

        barre_esp = pygame.image.load("barre_esp.png")  # Affichage de la barre espace
        barre_esp = pygame.transform.scale(barre_esp, (30, 10))
        barre_rect = barre_esp.get_rect()
        barre_rect.left = 300
        barre_rect.bottom = HEIGHT+40
        self.screen.blit(barre_esp,barre_rect) 
        
        fleches = pygame.image.load("fleches.png")  # Affichage des flèches
        fleches = pygame.transform.scale(fleches, (30, 20))
        fleches_rect = fleches.get_rect()
        fleches_rect.topleft = (0, HEIGHT)
        
        if moving:
            self.screen.blit(fleches,fleches_rect) 
            
            font = pygame.font.Font(None, 15)   # Afficher "Se déplacer"
            text_surface = font.render("Se déplacer", True, WHITE)
            text_rect = text_surface.get_rect()
            text_rect.bottomleft = fleches_rect.bottomright
            self.screen.blit(text_surface, text_rect)
            
            prev = pygame.image.load("un.png")   # Afficher les numéros des compétences
            prev = pygame.transform.scale(prev, (25, 25))
            prev_rect = prev.get_rect()
            prev_rect.bottomright = (0,HEIGHT+50)
            for chiffre,i in zip(["un.png", "deux.png", "trois.png", "quatre.png", "cinq.png"],unit.competences):
                img = pygame.image.load(chiffre) 
                img = pygame.transform.scale(img, (25, 25))
                img_rect = img.get_rect()
                img_rect.topleft = prev_rect.topright
                self.screen.blit(img, img_rect)
                prev_rect = img_rect
            
            font = pygame.font.Font(None, 15)
            text_surface = font.render("Séléctionner une compétence", True, WHITE)  # Afficher "Séléctionner une compétence"
            text_rect = text_surface.get_rect()
            text_rect.bottomleft = (prev_rect.topright[0] + 5, prev_rect.topright[1] + 25)
            self.screen.blit(text_surface, text_rect)
                 
            font = pygame.font.Font(None, 15)
            text_surface = font.render("Utiliser une compétence", True, WHITE)    # Afficher "Utiliser une compétence"
            text_rect = text_surface.get_rect()
            text_rect.bottomleft = barre_rect.bottomright
            self.screen.blit(text_surface, text_rect)
            
            # Afficher les cooldowns à droite
            cooldown_x = WIDTH - 150
            for i, comp in enumerate(unit.competences):
                cooldown_text = f"{comp.nom}: disponible dans {comp.current_cooldown}tours" if comp.current_cooldown > 0 else f"{comp.nom}: Ready"
                cooldown_surface = font.render(cooldown_text, True, WHITE)
                cooldown_rect = cooldown_surface.get_rect()
                cooldown_rect.topleft = (cooldown_x, HEIGHT + 5 + i * 20)
                self.screen.blit(cooldown_surface, cooldown_rect)
            
        if viser_mode:
            for c in unit.competences :
                if (c.is_selected == True) and (type(c) in [BouleDeFeu,Tir]):
                    self.screen.blit(fleches,fleches_rect) 
                         
                    font = pygame.font.Font(None, 15)
                    text_surface = font.render("Viser", True, WHITE)     # Afficher "Viser"
                    text_rect = text_surface.get_rect()
                    text_rect.bottomleft = fleches_rect.bottomright
                    self.screen.blit(text_surface, text_rect)
                    break
                 
            font = pygame.font.Font(None, 15)
            text_surface = font.render("Confirmer", True, WHITE)     # Afficher "Confirmer"
            text_rect = text_surface.get_rect()
            text_rect.bottomleft = barre_rect.bottomright
            self.screen.blit(text_surface, text_rect)
            
        enter = pygame.image.load("enter.png")                  # Afficher la touche "entrer"
        enter = pygame.transform.scale(enter, (20, 20))
        enter_rect = enter.get_rect()
        enter_rect.left = barre_rect.left
        enter_rect.top = HEIGHT
        self.screen.blit(enter,enter_rect) 
        
        font = pygame.font.Font(None, 15)
        text_surface = font.render("Finir le tour", True, WHITE)  # Afficher la touche "Finir le tour"
        text_rect = text_surface.get_rect()
        text_rect.bottomleft = enter_rect.bottomright
        self.screen.blit(text_surface, text_rect)
        
        # Afficher la compétence séléctionnée
        
        font = pygame.font.Font(None, 20)
        txt_surface = font.render("Compétence sélectionnée :", True, WHITE)  # Afficher la touche "Finir le tour"
        txt_rect = txt_surface.get_rect()
        txt_rect.left = enter_rect.right + 200
        txt_rect.top = HEIGHT + 10
        self.screen.blit(txt_surface, txt_rect)
        
        for c in unit.competences:
            if c.is_selected == True:
                
                font = pygame.font.Font(None, 15)
                text_surface = font.render(c.nom + ": " + "c.description", True, WHITE)  # Afficher la compétence sélectionnée et sa description
                text_rect = text_surface.get_rect()
                text_rect.top = txt_rect.bottom+5
                text_rect.centerx = txt_rect.centerx
                self.screen.blit(text_surface, text_rect)
                
                comp = c.image
                comp = pygame.transform.scale(comp, (25, 25))
                comp_rect = comp.get_rect()
                comp_rect.centery = text_rect.centery
                comp_rect.right = text_rect.left
                self.screen.blit(comp,comp_rect)
                
                break

    def flip_display(self, viser_mode=False, moving=False):
        """Affiche le jeu."""

        # Affiche le background
        background = pygame.image.load("sol.png") 
        background = pygame.transform.scale(background, (WIDTH, HEIGHT)) 
        self.screen.blit(background,(0,0)) 
        
        # Affiche les instructions :          
        for unit in self.player_units:
            if unit.is_selected == True:
                selected_unit = unit
                self.afficher_instructions(selected_unit,viser_mode,moving)
                break
        
        for case in self.cases :
            case.draw(self.screen)       
        
        # Affiche les unités
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen)
            
        if(moving):
            self.screen.blit(self.aim_surface, (0, 0))
            
        # Affiche la surface de visée sur l'écran
        if(viser_mode):
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

def main():

    pygame.init()
    pygame.mixer.init()

    #musique de l'interface
    pygame.mixer.music.load("son_interface.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)
    
    # Initialisation du jeu
    screen = pygame.display.set_mode((WIDTH, HEIGHT+50))
    pygame.display.set_caption("Monster Haven")

    # Étapes du jeu
    countdown_screen = CountdownScreen()
    main_menu = MainMenu()
    unit_selection_screen = UnitSelectionScreen()

    # Afficher le compte à rebours
    countdown_screen.countdown()

    # Afficher le menu principal
    if main_menu.display_menu() == "start_game":
        # Sélection des unités
        selected_units = unit_selection_screen.choose_unit(num_units_to_select=3)

        # Démarrer le jeu
        game = Game(screen)
        game.player_units = selected_units

        while True:
            game.handle_player_turn()
            game.handle_enemy_turn()
    

if __name__ == "__main__":
    main()
