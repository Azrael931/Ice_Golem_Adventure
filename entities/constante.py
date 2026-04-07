# ── Jeu ─────────────────────────────────────────────────
Resolution = 1024, 768
FPS        = 60

# ── Physique ─────────────────────────────────────────────
gravite = 0.6

# ── Joueur (side) ────────────────────────────────────────
player_speed  = 3.5
player_jump   = 12
player_spawn  = (100, 100)
player_hp_max = 100

# ── Joueur (top view) ────────────────────────────────────
player_speed_top  = 3
player_sprite_w   = 320    # taille affichée du sprite
player_sprite_h   = 320
player_hitbox_w   = 64     # hitbox de collision
player_hitbox_h   = 64
player_anim_speed = 0.14

# ── Attaques (top view) ──────────────────────────────────
attack1_damage        = 0.3    # dégâts/frame clic gauche
attack2_damage        = 0.8    # dégâts/frame clic droit
attack_hitbox_inflate = 100    # agrandissement hitbox en px

# ── Monstre Troll ────────────────────────────────────────
monster_sprite_w   = 128
monster_sprite_h   = 128
monster_hitbox_w   = 64
monster_hitbox_h   = 64
monster_hp_max     = 100
monster_anim_speed = 0.1
monster_spawn      = (400, 400)

# ── Map ──────────────────────────────────────────────────
fond_menu = 'assets/ui/fond_menu.png'
fond_n1   = 'assets/ui/fond_n1.png'
fond_n2   = 'assets/ui/fond_n2.png'
fond_n3   = 'assets/ui/fond_n3.png'

# ── Tir ──────────────────────────────────────────────────
tir_speed    = 20
tir_damage   = 10
tir_cooldown = 50

# ── Menu ─────────────────────────────────────────────────
bouton_jouer     = 'assets/ui/bouton_jouer_1.png'
bouton_jouer_2   = 'assets/ui/bouton_jouer_2.png'
bouton_setting   = 'assets/ui/bouton_parametre_1.png'
bouton_setting_2 = 'assets/ui/bouton_parametre_2.png'
bouton_retour    = 'assets/ui/bouton_retour_1.png'
bouton_retour_2  = 'assets/ui/bouton_retour_2.png'
musique_menu     = 'assets/audio/musique-menu.mp3'

# ── Projectile ───────────────────────────────────────────
projectile_vitesse   = 12
projectile_gravite   = 0.35
projectile_rayon     = 6
projectile_couleur   = (140, 210, 255)
projectile_contour   = (200, 240, 255)
projectile_duree_vie = 180

