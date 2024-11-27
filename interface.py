import pygame
import sys

# Constantes
WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (150, 150, 150)
FPS = 60

def display_menu(screen):
    """Affiche le menu principal et gère les interactions."""
    # Charger l'image de fond
    background_image = pygame.image.load("Valorant.jpg")  # Remplacez par le chemin d'une image valide
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Ajuster à la taille de l'écran

    font = pygame.font.Font(None, 48)
    menu_items = ["Nouvelle Partie", "Quitter"]
    selected_index = 0
    clock = pygame.time.Clock()

    while True:
        # Afficher l'image de fond
        screen.blit(background_image, (0, 0))

        # Dessiner les options du menu
        for i, item in enumerate(menu_items):
            color = WHITE if i == selected_index else GREY
            text_surface = font.render(item, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 60))
            screen.blit(text_surface, text_rect)

        pygame.display.flip()

        # Gestion des événements
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
                        return  # Quitte le menu pour lancer le jeu
                    elif selected_index == 1:  # "Quitter"
                        pygame.quit()
                        sys.exit()

        clock.tick(FPS)

def main():
    """Point d'entrée principal pour exécuter le programme."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Page d'accueil du jeu")

    # Appeler le menu principal
    display_menu(screen)

if __name__ == "__main__":
    main()
