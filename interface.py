import pygame
import sys
from unit import Archer, Paladin, Guerrier, Mage, WIDTH, HEIGHT, WHITE, GREY, FPS
import math

"""
@author: Amira
"""

class InterfaceBase:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT+50))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)

    def load_background(self, image_path):
        """Charge et ajuste l'image d'arrière-plan."""
        background = pygame.image.load(image_path)
        return pygame.transform.scale(background, (WIDTH, HEIGHT))


class CountdownScreen(InterfaceBase):
    def __init__(self):
        super().__init__()
        self.background_image = self.load_background("monster_haven.jpg")

    def countdown(self):
        """Affiche un compte à rebours sous forme de barre de chargement."""
        bar_width = 400
        bar_height = 30
        bar_x = (WIDTH - bar_width) // 2
        bar_y = (HEIGHT * 2) // 3

        percentage = 0

        while percentage < 1.0:
            self.screen.blit(self.background_image, (0, 0))

            # Barre de chargement
            pygame.draw.rect(self.screen, GREY, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width * percentage, bar_height))

            # Affichage du pourcentage
            text_surface = self.font.render(f"{int(percentage * 100)}%", True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, bar_y - 40))
            self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            percentage += 0.0167  # Vitesse du chargement
            self.clock.tick(60)


class MainMenu(InterfaceBase):
    def __init__(self):
        super().__init__()
        self.background_image = self.load_background("monster_haven.jpg")

    def display_menu(self):
        """Affiche le menu principal."""
        menu_items = ["Nouvelle partie", "Quitter"]
        selected_index = 0
        frame = 0

        while True:
            self.screen.blit(self.background_image, (0, 0))

            for i, item in enumerate(menu_items):
                color = WHITE if i == selected_index else GREY
                oscillation_offset = math.sin((frame + i * 10) / 20) * 5
                text_surface = self.font.render(item, True, color)
                text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3 + i * 60 + oscillation_offset))
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
                        if selected_index == 0:
                            return "start_game"
                        elif selected_index == 1:
                            pygame.quit()
                            sys.exit()
            frame += 1
            self.clock.tick(FPS)


class UnitSelectionScreen(InterfaceBase):
    def __init__(self):
        super().__init__()
        self.background_image = self.load_background("monster1.jpg")

    def choose_unit(self, num_units_to_select=3):
        """Permet au joueur de choisir les unités."""
        units = [
            {"name": "Paladin", "class": Paladin, "image": "paladin.png"},
            {"name": "Archer", "class": Archer, "image": "archer.png"},
            {"name": "Guerrier", "class": Guerrier, "image": "guerrier.png"},
            {"name": "Mage", "class": Mage, "image": "mage.png"}
        ]

        # Charger les icônes des unités
        for unit in units:
            unit["icon"] = pygame.image.load(unit["image"])
            unit["icon"] = pygame.transform.scale(unit["icon"], (280, 280))

        selected_index = 0
        selected_units = []  # Liste des unités sélectionnées
        frame = 0

        while len(selected_units) < num_units_to_select:
            self.screen.blit(self.background_image, (0, 0))

            # Affichage des unités disponibles
            for i, unit in enumerate(units):
                color = WHITE if i == selected_index else GREY
                oscillation_offset = math.sin((frame + i * 10) / 20) * 5
                text_surface = self.font.render(unit["name"], True, color)
                text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100 + i * 60 + oscillation_offset))
                self.screen.blit(text_surface, text_rect)

                if i == selected_index:
                    self.screen.blit(unit["icon"], (0, HEIGHT-280))  # Afficher l'icône

            # Afficher les unités déjà sélectionnées
            selected_text = f"Sélectionnées ({len(selected_units)}/{num_units_to_select}): " + ", ".join(
                [unit.name for unit in selected_units]  # Utilisation de l'attribut `name` de l'objet
            )
            selected_surface = self.font.render(selected_text, True, WHITE)
            selected_rect = selected_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
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
                    elif event.key == pygame.K_RETURN:
                        # Ajouter l'unité sélectionnée
                        selected_unit = units[selected_index]["class"](len(selected_units))
                        selected_unit.name = units[selected_index]["name"]  # Ajouter un attribut `name` à l'objet
                        selected_units.append(selected_unit)
                        # Réinitialiser l'index si nécessaire
                        if len(selected_units) < num_units_to_select:
                            selected_index = 0  # Réinitialiser l'index pour les unités restantes
                        else:
                            return selected_units
            frame += 1
            self.clock.tick(FPS)
