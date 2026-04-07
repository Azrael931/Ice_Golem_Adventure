import pygame
import os
import random

# -------------------------------------------------------
# CINEMATIQUE 1 : Logo avec fondu
# -------------------------------------------------------
def cinematique_logo(fenetre):
    """
    Affiche le logo avec un effet de fondu.
    Retourne True si terminé normalement, False si l'utilisateur quitte.
    """
    logo = pygame.image.load('assets/ice_logo.png').convert_alpha()

    screen_w, screen_h = fenetre.get_size()
    logo_w, logo_h = logo.get_size()

    max_w = screen_w * 0.8
    max_h = screen_h * 0.8
    if logo_w > max_w or logo_h > max_h:
        ratio = min(max_w / logo_w, max_h / logo_h)
        logo = pygame.transform.scale(logo, (int(logo_w * ratio), int(logo_h * ratio)))
        logo_w, logo_h = logo.get_size()

    logo_rect = logo.get_rect(center=(screen_w // 2, screen_h // 2))

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
                return True

        alpha -= 5
        if alpha < 0:
            alpha = 0

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
        if alpha > 255:
            alpha = 255

        fenetre.fill((0, 0, 0))
        fenetre.blit(logo, logo_rect)
        fond_noir.set_alpha(alpha)
        fenetre.blit(fond_noir, (0, 0))
        pygame.display.flip()
        horloge.tick(60)

    return True


# -------------------------------------------------------
# CINEMATIQUE 2 : Intro avec monologue
# -------------------------------------------------------

# Liste des lignes du monologue du scientifique
MONOLOGUE = [
    "Systeme de messagerie d'urgence active...",
    "Si tu recois ce message, c'est que je suis",
    "probablement... deja disparu.",
    "",
    "Je suis le Professeur Snow.",
    "J'etais chercheur a la Station Polaire Omega.",
    "",
    "Une experience a mal tourne.",
    "Une creature de pollution colossale a ete creee :",
    "Smog....",
    "",
    "Il a detruit la station... et il menace",
    "maintenant le monde entier.",
    "",
    "Toi seul peux l'arreter.",
    "Traverse les ruines,",
    "récupère les pièces de la machine....,",
    "pour le detruire....,",
    "",
    "Le destin du monde repose sur toi.",
    "Bonne chance... Imir...",
]


def _dessiner_boite_texte(fenetre, police, lignes_affichees, alpha_boite):
    """Dessine la boite de dialogue semi-transparente avec le texte."""
    screen_w, screen_h = fenetre.get_size()

    # Dimensions de la boite
    boite_h = 220
    boite_y = screen_h - boite_h - 20
    boite_rect = pygame.Rect(30, boite_y, screen_w - 60, boite_h)

    # Fond semi-transparent de la boite
    boite_surf = pygame.Surface((boite_rect.width, boite_rect.height))
    boite_surf.fill((5, 15, 40))
    boite_surf.set_alpha(alpha_boite)
    fenetre.blit(boite_surf, (boite_rect.x, boite_rect.y))

    # Bordure lumineuse bleue
    pygame.draw.rect(fenetre, (80, 180, 255), boite_rect, 2)
    pygame.draw.rect(fenetre, (40, 100, 200), boite_rect.inflate(4, 4), 1)

    # Nom du personnage
    nom_surf = police.render(">>> Professeur Snow <<<", True, (120, 200, 255))
    fenetre.blit(nom_surf, (boite_rect.x + 15, boite_rect.y + 10))

    # Lignes de texte
    ligne_y = boite_rect.y + 40
    for ligne in lignes_affichees:
        if ligne == "":
            ligne_y += 12
            continue
        texte_surf = police.render(ligne, True, (200, 230, 255))
        fenetre.blit(texte_surf, (boite_rect.x + 15, ligne_y))
        ligne_y += 22

    # Indicateur "Appuyez sur ESPACE"
    ticks = pygame.time.get_ticks()
    if (ticks // 600) % 2 == 0:
        hint_surf = police.render("[ ESPACE ] Continuer    [ ECHAP ] Passer", True, (100, 150, 220))
        fenetre.blit(hint_surf, (boite_rect.x + 15, boite_rect.bottom - 28))


def _creer_son_frappe():
    """
    Genere un son de frappe machine a ecrire synthetique court (bruit blanc ~30ms).
    Retourne un objet pygame.mixer.Sound ou None si le mixer n'est pas disponible.
    """
    freq = 44100
    duree_ms = 30
    nb_echantillons = freq * duree_ms // 1000  # ~1323 echantillons
    buf = bytearray(nb_echantillons * 2)  # 16 bits = 2 octets par echantillon
    i = 0
    while i < nb_echantillons:
        # Bruit blanc court avec enveloppe decroissante (plus fort au debut)
        facteur = 1.0 - (i / nb_echantillons)
        valeur = int(random.randint(-3000, 3000) * facteur)
        # Ecrire 16 bits little-endian
        buf[i * 2] = valeur & 0xFF
        buf[i * 2 + 1] = (valeur >> 8) & 0xFF
        i += 1
    son = pygame.mixer.Sound(buffer=bytes(buf))
    son.set_volume(0.15)
    return son


def cinematique_intro(fenetre):
    """
    Affiche la cinematique d'intro avec l'image du scientifique holographique
    et le monologue du Professeur Snow.
    Retourne True si terminé normalement, False si l'utilisateur quitte.
    """
    screen_w, screen_h = fenetre.get_size()

    # Son de frappe machine a ecrire (genere synthetiquement)
    son_frappe = _creer_son_frappe()

    # Chargement de l'image de fond (avec fallback si l'image n'existe pas)
    if os.path.exists('assets/holo-cine-labo.png'):
        fond = pygame.image.load('assets/holo-cine-labo.png').convert()
    else:
        fond = pygame.image.load('assets/fond_menu.png').convert()
    fond = pygame.transform.scale(fond, (screen_w, screen_h))

    # Overlay sombre pour améliorer la lisibilité du texte
    overlay = pygame.Surface((screen_w, screen_h))
    overlay.fill((0, 5, 20))
    overlay.set_alpha(80)

    # Police
    pygame.font.init()
    police = pygame.font.SysFont("Consolas", 18, bold=False)

    fond_noir = pygame.Surface((screen_w, screen_h))
    fond_noir.fill((0, 0, 0))

    horloge = pygame.time.Clock()

    # --- Fade In depuis le noir ---
    alpha = 255
    while alpha > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True  # Passer toute la cinematique
        alpha -= 4
        if alpha < 0:
            alpha = 0
        fenetre.blit(fond, (0, 0))
        fenetre.blit(overlay, (0, 0))
        fond_noir.set_alpha(alpha)
        fenetre.blit(fond_noir, (0, 0))
        pygame.display.flip()
        horloge.tick(60)

    # --- Fade In de la boite de texte ---
    alpha_boite = 0
    while alpha_boite < 200:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
        alpha_boite += 8
        if alpha_boite > 200:
            alpha_boite = 200
        fenetre.blit(fond, (0, 0))
        fenetre.blit(overlay, (0, 0))
        _dessiner_boite_texte(fenetre, police, [], alpha_boite)
        pygame.display.flip()
        horloge.tick(60)

    # --- Affichage du monologue ligne par ligne (effet machine a ecrire) ---
    MAX_LIGNES_VISIBLES = 7  # Nombre max de lignes dans la boite
    lignes_affichees = []
    indice_ligne = 0
    char_affiche = 0
    compteur_frames = 0
    FRAMES_PAR_CHAR = 4 #Vitesse d'affichage des caracteres

    en_cours = True
    while en_cours and indice_ligne < len(MONOLOGUE):
        ligne_courante = MONOLOGUE[indice_ligne]
        ligne_complete = False

        # Afficher la ligne lettre par lettre
        while not ligne_complete:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        # Afficher la ligne directement en entier
                        char_affiche = len(ligne_courante)

            compteur_frames += 1
            if compteur_frames >= FRAMES_PAR_CHAR:
                compteur_frames = 0
                if char_affiche < len(ligne_courante):
                    # Jouer le son uniquement sur les caracteres visibles (pas les espaces)
                    c = ligne_courante[char_affiche]
                    if c != " " and son_frappe is not None:
                        son_frappe.play()
                char_affiche += 1
            if char_affiche >= len(ligne_courante):
                char_affiche = len(ligne_courante)
                ligne_complete = True

            texte_partiel = ligne_courante[:char_affiche]

            # Construire la liste d'affichage
            lignes_visibles = lignes_affichees[-MAX_LIGNES_VISIBLES:]
            if texte_partiel or ligne_courante == "":
                lignes_a_montrer = lignes_visibles + [texte_partiel]
            else:
                lignes_a_montrer = lignes_visibles

            fenetre.blit(fond, (0, 0))
            fenetre.blit(overlay, (0, 0))
            _dessiner_boite_texte(fenetre, police, lignes_a_montrer[-MAX_LIGNES_VISIBLES:], 200)
            pygame.display.flip()
            horloge.tick(60)

        # Ligne terminée : l'ajouter a l'historique
        lignes_affichees.append(ligne_courante)
        char_affiche = 0
        indice_ligne += 1

        # Petite pause entre les lignes (sauf lignes vides)
        if ligne_courante != "":
            pause = 600  # ms
        else:
            pause = 150

        temps = pygame.time.get_ticks()
        attente = True
        while attente and pygame.time.get_ticks() - temps < pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        attente = False  # Passer a la ligne suivante
            fenetre.blit(fond, (0, 0))
            fenetre.blit(overlay, (0, 0))
            lignes_visibles = lignes_affichees[-MAX_LIGNES_VISIBLES:]
            _dessiner_boite_texte(fenetre, police, lignes_visibles, 200)
            pygame.display.flip()
            horloge.tick(60)

    # --- Affichage final : attendre confirmation du joueur ---
    if indice_ligne >= len(MONOLOGUE):
        lignes_visibles = lignes_affichees[-MAX_LIGNES_VISIBLES:]
        en_attente = True
        while en_attente:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        en_attente = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    en_attente = False
            fenetre.blit(fond, (0, 0))
            fenetre.blit(overlay, (0, 0))
            _dessiner_boite_texte(fenetre, police, lignes_visibles, 200)
            pygame.display.flip()
            horloge.tick(60)

    # --- Fade Out vers le noir ---
    alpha = 0
    while alpha < 255:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        alpha += 5
        if alpha > 255:
            alpha = 255
        fenetre.blit(fond, (0, 0))
        fenetre.blit(overlay, (0, 0))
        fond_noir.set_alpha(alpha)
        fenetre.blit(fond_noir, (0, 0))
        pygame.display.flip()
        horloge.tick(60)

    return True

