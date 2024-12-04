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
        """Affiche un compte à rebours sous forme de barre rectangulaire avant d'accéder au menu."""
        start_time = pygame.time.get_ticks()
        duration = 5000  # 5 secondes en millisecondes

        bar_width = 400
        bar_height = 30
        bar_x = (WIDTH - bar_width) // 2
        bar_y = (HEIGHT - bar_height) // 2

        while True:
            elapsed_time = pygame.time.get_ticks() - start_time
            percentage = min(elapsed_time / duration, 1)

            self.screen.blit(self.background_image, (0, 0))
            pygame.draw.rect(self.screen, GREY, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width * percentage, bar_height))

            text_surface = self.font.render(f"{int(percentage * 100)}%", True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, bar_y - 40))
            self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            if elapsed_time >= duration:
                break

            self.clock.tick(FPS)

    def choose_units(self):
        """Permet au joueur de choisir ses unités."""
        units = [
            {"name": "Guerrier", "class": guerrier, "description": "Unité robuste avec des compétences de mêlée."},
            {"name": "Archer", "class": archer, "description": "Unité à distance avec des tirs précis."},
            {"name": "Mage", "class": mage, "description": "Unité magique avec des compétences de soin."},
            {"name": "Paladin", "class": paladin, "description": "Unité polyvalente avec des capacités défensives."}
        ]

        selected_units = []
        selected_index = 0

        while True:
            self.screen.blit(self.background_image, (0, 0))

            for i, unit in enumerate(units):
                color = WHITE if i == selected_index else GREY
                text_surface = self.font.render(unit["name"], True, color)
                text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 60))
                self.screen.blit(text_surface, text_rect)

            description = units[selected_index]["description"]
            description_surface = self.font.render(description, True, WHITE)
            description_rect = description_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            self.screen.blit(description_surface, description_rect)

            selected_text = "Sélectionnées: " + ", ".join(u["name"] for u in selected_units)
            selected_surface = self.font.render(selected_text, True, WHITE)
            selected_rect = selected_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 160))
            self.screen.blit(selected_surface, selected_rect)

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
                    elif event.key == pygame.K_RETURN:  # Ajouter une unité sélectionnée
                        if len(selected_units) < 4:
                            selected_units.append(units[selected_index])
                    elif event.key == pygame.K_BACKSPACE:  # Retourner au menu principal
                        return selected_units

            self.clock.tick(FPS)

    def display_menu(self):
        """Affiche le menu principal et gère les interactions."""
        self.countdown()

        menu_items = ["Nouvelle Partie", "Choisir les unités", "Quitter"]
        selected_index = 0
        chosen_units = []

        while True:
            self.screen.blit(self.background_image, (0, 0))

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
                            return chosen_units  # Retourner les unités sélectionnées
                        elif selected_index == 1:  # "Choisir les unités"
                            chosen_units = self.choose_units()
                        elif selected_index == 2:  # "Quitter"
                            pygame.quit()
                            sys.exit()
