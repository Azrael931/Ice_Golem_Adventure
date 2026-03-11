import pygame

def cinematique_logo(fenetre):
    """
    Affiche le logo avec un effet de fondu.
    Retourne True si terminé normalement, False si l'utilisateur quitte.
    """
    # Chargement du logo
    logo = pygame.image.load('assets/ice_logo.png').convert_alpha()

    # Redimensionner le logo si nécessaire pour qu'il tienne dans l'écran
    screen_w, screen_h = fenetre.get_size()
    logo_w, logo_h = logo.get_size()
    
    # Scale si trop grand
    max_w = screen_w * 0.8
    max_h = screen_h * 0.8
    if logo_w > max_w or logo_h > max_h:
        ratio = min(max_w / logo_w, max_h / logo_h)
        logo = pygame.transform.scale(logo, (int(logo_w * ratio), int(logo_h * ratio)))
        logo_w, logo_h = logo.get_size()

    logo_rect = logo.get_rect(center=(screen_w // 2, screen_h // 2))
    
    # Surface pour l'effet de fondu
    fond_noir = pygame.Surface((screen_w, screen_h))
    fond_noir.fill((0, 0, 0))
    
    horloge = pygame.time.Clock()
    
    # --- Phase 1 : Fade In ---
    alpha = 255
    while alpha > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return True # Skip cinématique
        
        alpha -= 5
        if alpha < 0: alpha = 0
            
        fenetre.fill((0, 0, 0))
        fenetre.blit(logo, logo_rect)
        
        fond_noir.set_alpha(alpha)
        fenetre.blit(fond_noir, (0, 0))
        
        pygame.display.flip()
        horloge.tick(60)
        
    # --- Phase 2 : Attente ---
    temps_debut = pygame.time.get_ticks()
    while pygame.time.get_ticks() - temps_debut < 2000:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return True
        
        pygame.display.flip()
        horloge.tick(60)
        
    # --- Phase 3 : Fade Out ---
    alpha = 0
    while alpha < 255:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return True
        
        alpha += 5
        if alpha > 255: alpha = 255
            
        fenetre.fill((0, 0, 0))
        fenetre.blit(logo, logo_rect)
        
        fond_noir.set_alpha(alpha)
        fenetre.blit(fond_noir, (0, 0))
        
        pygame.display.flip()
        horloge.tick(60)
        
    return True
