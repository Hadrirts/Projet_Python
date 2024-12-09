import pygame
import sys
from unit import *  # Importer les classes d'unités


class Interface:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Page d'accueil du jeu")
        self.clock = pygame.time.Clock()
        self.background_image = pygame.image.load("monster.jpg")
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))
        self.font = pygame.font.Font(None, 48)

    def countdown(self):
        """Affiche un compte à rebours sous forme de barre de chargement réaliste."""
        bar_width = 400
        bar_height = 30
        bar_x = (WIDTH - bar_width) // 2
        bar_y = (HEIGHT - bar_height) // 2

        checkpoints = [0.3, 0.6, 0.8, 1.0]  # Étapes de progression (30%, 60%, 80%, 100%)
        current_checkpoint = 0  # Index de l'étape actuelle
        percentage = 0  # Pourcentage initial

        while percentage < 1.0:
            self.screen.blit(self.background_image, (0, 0))
            
            # Barre grise de fond
            pygame.draw.rect(self.screen, GREY, (bar_x, bar_y, bar_width, bar_height))
            # Barre blanche remplie selon le pourcentage
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width * percentage, bar_height))
            
            # Afficher le pourcentage en texte
            text_surface = self.font.render(f"{int(percentage * 100)}%", True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, bar_y - 40))
            self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            
            # Avancer progressivement jusqu'à la prochaine étape
            if percentage < checkpoints[current_checkpoint]:
                percentage += 0.01  # Avancement progressif
            else:
                pygame.time.delay(500)  # Petite pause réaliste (500 ms)
                current_checkpoint += 1  # Passer à l'étape suivante

            self.clock.tick(FPS)

    def choose_units(self):
        """Permet au joueur de choisir une unité et démarre le jeu immédiatement."""
        units = [
            {"name": "Guerrier", "class": guerrier, "description": "Unité robuste avec des compétences de mêlée."},
            {"name": "Archer", "class": archer, "description": "Unité à distance avec des tirs précis."},
            {"name": "Mage", "class": mage, "description": "Unité magique avec des compétences de soin."},
            {"name": "Paladin", "class": paladin, "description": "Unité polyvalente avec des capacités défensives."}
        ]

        selected_index = 0

        while True:
            self.screen.blit(self.background_image, (0, 0))

            # Afficher la liste des unités
            for i, unit in enumerate(units):
                color = WHITE if i == selected_index else GREY
                text_surface = self.font.render(unit["name"], True, color)
                text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 60))
                self.screen.blit(text_surface, text_rect)

            # Afficher la description de l'unité sélectionnée
            description = units[selected_index]["description"]
            description_surface = self.font.render(description, True, WHITE)
            description_rect = description_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            self.screen.blit(description_surface, description_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(units)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(units)
                    elif event.key == pygame.K_RETURN:  # Valider l'unité sélectionnée
                        selected_unit_class = units[selected_index]["class"]
                        return selected_unit_class(0, 0, 100, 20, "player")  # Créer une instance d'unité et la retourner

            self.clock.tick(FPS)

    def display_menu(self):
        """Affiche le menu principal avec l'option de choisir une unité et démarrer directement le jeu."""
        self.countdown()

        menu_items = ["Nouvelle Partie", "Quitter"]
        selected_index = 0

        while True:
            self.screen.blit(self.background_image, (0, 0))

            # Afficher les options du menu
            for i, item in enumerate(menu_items):
                color = WHITE if i == selected_index else GREY
                text_surface = self.font.render(item, True, color)
                text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 60))
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(menu_items)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(menu_items)
                    elif event.key == pygame.K_RETURN:
                        if selected_index == 0:  # "Nouvelle Partie"
                            return self.choose_units()  # Passer directement à la sélection d'unité
                        elif selected_index == 1:  # "Quitter"
                            pygame.quit()
                            sys.exit()
