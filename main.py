import pygame
import os
import sys

def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

#initialse pygame
pygame.init()

#window dimensions
WIDTH = 900
HEIGHT = 600

#create game window
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Abyss: A Journey Through The Underworld")

#environment images
background = pygame.image.load(
    resource_path("assets/abyss_environment_assets/background.png")
   ).convert_alpha()

midground = pygame.image.load(
    resource_path("assets/abyss_environment_assets/midground.png")
).convert_alpha()

back_objects_sheet = pygame.image.load(
    resource_path("assets/abyss_environment_assets/back_objects.png")
).convert_alpha()

foreground_sheet = pygame.image.load(
    resource_path("assets/abyss_environment_assets/foreground.png")
).convert_alpha()

tiles_sheet = pygame.image.load(
    resource_path("assets/abyss_environment_assets/tiles.png")
).convert_alpha()

#player sprites
player_fast_sheet = pygame.image.load(
   resource_path( "assets/abyss_environment_assets/player-fast.png")
).convert_alpha()


def load_player_frames(sheet):
    frame_width = sheet.get_width() // 5
    frame_height = sheet.get_height()

    frames = []

    for i in range(5):
        frame = sheet.subsurface(
            (i * frame_width, 0, frame_width, frame_height)
        ).copy()

        bounds = frame.get_bounding_rect()

        if bounds.width > 0 and bounds.height > 0:
            frame = frame.subsurface(bounds).copy()

        #fit every frame in same canvas
        scale = min(
            36 / frame.get_width(),
            36 / frame.get_height()
        )

        new_size = (
            max(1, int(frame.get_width() * scale)),
            max(1, int(frame.get_height() * scale))
        )

        frame = pygame.transform.scale(frame, new_size)

        canvas = pygame.Surface((40, 40), pygame.SRCALPHA)
        canvas.blit(
            frame,
            frame.get_rect(center=(20, 20))
        )

        frames.append(canvas)

    return frames


player_fast_frames = load_player_frames(player_fast_sheet)

#directional sprites
player_frames = {
    "right": player_fast_frames,
    "left": [
        pygame.transform.flip(frame, True, False)
        for frame in player_fast_frames
    ],
    "up": [
        pygame.transform.rotate(frame, 90)
        for frame in player_fast_frames
    ],
    "down": [
        pygame.transform.rotate(frame, -90)
        for frame in player_fast_frames
    ]
}

player_direction = "right"
player_frame_index = 0
player_animation_timer = 0  


#scale images
def scale_environment(image): 
    original_width,original_height = image.get_size()

    scale = max(
        WIDTH / original_width,
        HEIGHT / original_height
    )

    new_width = int(original_width*scale)
    new_height = int(original_height*scale)

    image = pygame.transform.scale(
        image, (new_width,new_height)
    )

    #crop center
    x = (new_width - WIDTH) // 2
    y = (new_height - HEIGHT) // 2

    return image.subsurface(
        (x,y,WIDTH,HEIGHT)
    ).copy()

   

terrain = tiles_sheet.subsurface(
    pygame.Rect(720, 244, 1168, 772)
).copy()

terrain = pygame.transform.scale(
    terrain, (900, 595)
)
    
background = scale_environment(background)
midground = scale_environment(midground)

#load enemy animations
def load_fish_frames(filename,scale=2):
    sheet = pygame.image.load(filename).convert_alpha()

    sheet_width,sheet_height = sheet.get_size()

    frame_width = sheet_width // 4
    frames = []

    for i in range(4):
        frame = sheet.subsurface(
            pygame.Rect(
                i* frame_width,
                0,
                frame_width,
                sheet_height
            )
        ).copy()

        frame = pygame.transform.scale(
            frame,
            (frame_width * scale, sheet_height * scale)
        )

        frames.append(frame)

    return frames

#load individ enemies
fish_frames = load_fish_frames(
    resource_path("assets/abyss_environment_assets/enemies/fish.png")
)

dart_fish_frames = load_fish_frames(
    resource_path("assets/abyss_environment_assets/enemies/fish-dart.png")
)

big_fish_frames = load_fish_frames(
    resource_path("assets/abyss_environment_assets/enemies/fish-big.png")
)

#enem/guardian animation
guardian_frame_index = 0
guardian_animation_timer = 0
guardian_animation_speed = 0.15

#guardian movement
guardian_x = WIDTH - 120
guardian_y = HEIGHT // 2 - 100

guardian_direction = -1
guardian_speed = 90

#guardian detection
guardian_detection_radius = 180
guardian_chasing = False
guardian_stop_distance = 65

#resize
def resize_object(image,factor):
    width,height = image.get_size()

    return pygame.transform.scale(
        image,
        (int(width*factor), int(height*factor))
    )

#extract decor objs
pillar_1 = back_objects_sheet.subsurface(
    pygame.Rect(228, 0 ,120,231)
).copy()

pillar_2 = back_objects_sheet.subsurface(
    pygame.Rect(70,1,92,231)
).copy()

ruined_arch = back_objects_sheet.subsurface(
    pygame.Rect(495,32,245,186)
).copy()

pillar_3 = back_objects_sheet.subsurface(
    pygame.Rect(0,587,120,231)
).copy()

#extract foreground objs
coral_arch_1 = foreground_sheet.subsurface(
    pygame.Rect(125,602,198,205)
).copy()
coral_arch_2 = foreground_sheet.subsurface(
    pygame.Rect(600,556,198,205)
).copy()
foreground_plant = foreground_sheet.subsurface(
    pygame.Rect(1163,0,52,67)
).copy()
foreground_rock = foreground_sheet.subsurface(
    pygame.Rect(971,660,85,98)
).copy()

#resize foreground objs
coral_arch_1 = resize_object(coral_arch_1,0.65)
coral_arch_2 = resize_object(coral_arch_2,0.65)
foreground_plant = resize_object(foreground_plant,1.5)
foreground_rock = resize_object(foreground_rock,0.8)

#game clock
clock = pygame.time.Clock()

#player settings
PLAYER_SIZE = 32
PLAYER_SPEED = 240

#create player
player=pygame.Rect(
    WIDTH // 2,
    HEIGHT // 2,
    PLAYER_SIZE,
    PLAYER_SIZE
)

#lvl progression
level = 1
fragments_collected = 0
victory = False

#lvl transition
transitioning = False
transition_alpha = 0
transition_speed = 300
transition_phase = "fade_out"
transition_timer = 0

level_names = [
    "The Forgotten Reef",
    "The Sunken City",
    "The Abyssal Chamber"
]

fragment_positions = [
    (WIDTH - 130,HEIGHT //2),
    (120,180),
    (WIDTH //2,150)
]

fragment = pygame.Rect(
    *fragment_positions[0],
    24,
    24
)


fragment_collected = False
fragments_collected = 0

#oxygen tank
MAX_OXYGEN = 100
oxygen = MAX_OXYGEN
OXYGEN_DRAIN = 5
game_over = False

#screen states
game_started = False

start_button = pygame.Rect(350, 350, 200, 55)
restart_button = pygame.Rect(350, 390, 200, 55)

title_font = pygame.font.SysFont(None, 85)
button_font = pygame.font.SysFont(None, 38)
GUARDIAN_DAMAGE = 10
GUARDIAN_HIT_COOLDOWN = 1.0
guardian_hit_timer = 0

def draw_reef(screen):

    #ocean bg
    screen.blit(background, (0,0))
    screen.blit(midground, (0,0)) 
    screen.blit(terrain,(0,5))


#draw artifact
def draw_artifact(surface, rect):

    cx, cy = rect.center

    #outer glow
    for radius, alpha in [(25, 25), (19, 45), (13, 70)]:
        glow = pygame.Surface(
            (radius * 2, radius * 2),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            glow,
            (30, 210, 230, alpha),
            (radius, radius),
            radius
        )

        surface.blit(
            glow,
            (cx - radius, cy - radius)
        )

    #main shape
    outer_points = [
        (cx, cy - 19),
        (cx + 13, cy - 5),
        (cx + 9, cy + 14),
        (cx, cy + 21),
        (cx - 9, cy + 14),
        (cx - 13, cy - 5)
    ]

    pygame.draw.polygon(
        surface,
        (40, 205, 220),
        outer_points
    )

    #golden inner crystal
    inner_points = [
        (cx, cy - 13),
        (cx + 8, cy - 4),
        (cx + 5, cy + 11),
        (cx, cy + 15),
        (cx - 5, cy + 11),
        (cx - 8, cy - 4)
    ]

    pygame.draw.polygon(
        surface,
        (245, 190, 65),
        inner_points
    )

    #inner highlight
    pygame.draw.polygon(
        surface,
        (255, 230, 145),
        [
            (cx, cy - 10),
            (cx + 4, cy - 3),
            (cx, cy + 3),
            (cx - 4, cy - 3)
        ]
    )

    #small cyan centre
    pygame.draw.circle(
        surface,
        (130, 245, 255),
        (cx, cy + 5),
        3
    )

    #outline
    pygame.draw.polygon(
        surface,
        (150, 250, 255),
        outer_points,
        2
    )

#main game loop
running = True
next_level = 1

while running:

    dt = clock.tick(60) / 1000
    guardian_hit_timer = max(0, guardian_hit_timer - dt)

    #select guardian for lvl
    if level == 1:
        guardian_frames = fish_frames
        guardian_speed = 80
        guardian_stop_distance = 65

    elif level == 2:
        guardian_frames = dart_fish_frames
        guardian_speed = 150
        guardian_stop_distance = 75

    else:
        guardian_frames = big_fish_frames
        guardian_speed = 110
        guardian_stop_distance = 90

    #guardian animation
    guardian_animation_timer += dt

    if guardian_animation_timer >= guardian_animation_speed:
        guardian_frame_index += 1
        guardian_animation_timer = 0

        if guardian_frame_index >= len(guardian_frames):
            guardian_frame_index = 0

    guardian_image = guardian_frames[guardian_frame_index]

    #handle events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            mouse_pos = event.pos

            #start button
            if not game_started and start_button.collidepoint(mouse_pos):
                game_started = True

            #restart button
            elif (game_over or victory) and restart_button.collidepoint(mouse_pos):

                game_started = True
                game_over = False
                victory = False

                level = 1
                next_level = 1
                fragments_collected = 0
                oxygen = MAX_OXYGEN

                transitioning = False
                transition_alpha = 0
                transition_phase = "fade_out"
                transition_timer = 0

                player.center = (WIDTH // 2, HEIGHT // 2)

                #reset fragment 
                fragment = pygame.Rect(
                    *fragment_positions[0], 24, 24
                )

                fragment_collected = False

                #reset position the Lvl1 guardian
                guardian_x = (
                    fragment.centerx - fish_frames[0].get_width() / 2
                )

                guardian_y = (
                    fragment.centery - fish_frames[0].get_height() - 45
                )

                guardian_direction = 1
                guardian_chasing = False
                guardian_hit_timer = 0
                guardian_frame_index = 0
                guardian_animation_timer = 0
    
    #gameplay
    if game_started and not game_over and not victory:

        # OXYGEN DEPLETION
        oxygen -= OXYGEN_DRAIN * dt
        oxygen = max(0, oxygen)

        if oxygen <= 0:
            game_over = True

                     
        #get player input
        keys = pygame.key.get_pressed()
        movement = pygame.Vector2(0, 0)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            movement.x -= 1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            movement.x += 1

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            movement.y -= 1

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            movement.y += 1

        if movement.length_squared() > 0:
            movement = movement.normalize()
    
       #player movement n animation

        if movement.length_squared() > 0:

            if abs(movement.x) >= abs(movement.y):
                player_direction = "right" if movement.x > 0 else "left"
            else:
                player_direction = "down" if movement.y > 0 else "up"

            player_animation_timer += dt

            if player_animation_timer >= 0.12:
                player_frame_index = (
                    player_frame_index + 1
                ) % 5

                player_animation_timer = 0

        else:
            player_frame_index = 0
            player_animation_timer = 0

        player.x += int(movement.x * PLAYER_SPEED * dt)
        player.y += int(movement.y * PLAYER_SPEED * dt)

        player.clamp_ip(pygame.Rect(0, 160, WIDTH, HEIGHT - 160))
        
        #guardian movement
        if not transitioning and not game_over:

            guardian_width = guardian_image.get_width()
            guardian_height = guardian_image.get_height()

            #guardian's home - above artifact,never inside the HUD area.
            guardian_home_x = (
                fragment.centerx - guardian_width / 2
            )

            guardian_home_y = max(
                170,
                fragment.centery - guardian_height - 45
            )

            guardian_home_x = max(
                10,
                min(WIDTH - guardian_width - 10, guardian_home_x)
            )

            guardian_home_y = min(
                HEIGHT - guardian_height - 10,
                guardian_home_y
            )

            #player detection is based on proximity to artifact
            player_center = pygame.Vector2(player.center)
            artifact_center = pygame.Vector2(fragment.center)

            distance_to_artifact = player_center.distance_to(
                artifact_center
            )

            detection = guardian_detection_radius

            if level == 2:
                detection *= 1.15
            elif level == 3:
                detection *= 1.3

            guardian_chasing = (
                distance_to_artifact <= detection
            )

            guardian_pos = pygame.Vector2(
                guardian_x, guardian_y
            )

            if guardian_chasing:

                #chase the player, but never enter the HUD
                target = pygame.Vector2(
                    player.centerx,
                    max(170 + guardian_height / 2,
                        player.centery)
                )

                direction = target - (
                    guardian_pos + pygame.Vector2(
                        guardian_width / 2,
                        guardian_height / 2
                    )
                )

                if direction.length() > 5:
                    direction = direction.normalize()

                    guardian_x += direction.x * guardian_speed * dt
                    guardian_y += direction.y * guardian_speed * dt

                    if direction.x < 0:
                        guardian_direction = -1
                    elif direction.x > 0:
                        guardian_direction = 1

            else:

                #patrol area around the artifact
                left_limit = max(
                    10, guardian_home_x - 60
                )

                right_limit = min(
                    WIDTH - guardian_width - 10,
                    guardian_home_x + 60
                )

                #return if outside patrol area or too far vertically
                if (
                    guardian_y < guardian_home_y - 8
                    or guardian_y > guardian_home_y + 8
                    or guardian_x < left_limit
                    or guardian_x > right_limit
                ):

                    target_x = max(
                        left_limit,
                        min(right_limit, guardian_home_x)
                    )

                    direction = pygame.Vector2(
                        target_x - guardian_x,
                        guardian_home_y - guardian_y
                    )

                    if direction.length() > 5:
                        direction = direction.normalize()

                        guardian_x += direction.x * guardian_speed * dt
                        guardian_y += direction.y * guardian_speed * dt

                else:

                    #patrol horizontally
                    guardian_x += (
                        guardian_direction * guardian_speed * 0.3 * dt
                    )

                    if guardian_x <= left_limit:
                        guardian_x = left_limit
                        guardian_direction = 1

                    elif guardian_x >= right_limit:
                        guardian_x = right_limit
                        guardian_direction = -1

            #final screen boundaries
            guardian_y = max(
                160,
                min(
                    HEIGHT - guardian_height - 10,
                    guardian_y
                )
            )
      
       
        #collect fragment
        if (
            not transitioning
            and not fragment_collected
            and player.colliderect(fragment)
        ):

            fragment_collected = True
            fragments_collected += 1

            if level < 3:

                next_level = level + 1

                transitioning = True
                transition_alpha = 0
                transition_phase = "fade_out"

            else:
                victory = True

       
        #lvl transition update
        if transitioning:

            if transition_phase == "fade_out":

                transition_alpha += transition_speed * dt

                if transition_alpha >= 255:

                    transition_alpha = 255

                    #move to next lvl
                    level = next_level

                    oxygen = MAX_OXYGEN

                    guardian_direction = -1
                    guardian_chasing = False
                    guardian_frame_index = 0
                    guardian_animation_timer = 0

                    player.center = (WIDTH // 2, HEIGHT // 2)

                    fragment = pygame.Rect(
                        *fragment_positions[level - 1], 24, 24
                    )
                      #spawn guardian above the artifact
                    if level == 1:
                        spawn_frames = fish_frames
                    elif level == 2:
                        spawn_frames = dart_fish_frames
                    else:
                        spawn_frames = big_fish_frames

                    guardian_x = (
                        fragment.centerx - spawn_frames[0].get_width() / 2
                    )

                    guardian_y = (
                        fragment.centery - spawn_frames[0].get_height() - 45
                    )

                    guardian_direction = -1

                    fragment_collected = False

                    #start fade in
                    transition_phase = "fade_in"

            elif transition_phase == "fade_in":

                transition_alpha -= transition_speed * dt

                if transition_alpha <= 0:

                    transition_alpha = 0
                    transitioning = False

    #drawing

    #background
    draw_reef(screen)
    
    #draw guardian
    if guardian_direction == -1:

        displayed_guardian = pygame.transform.flip(
            guardian_image, True, False
        )

    else:
        displayed_guardian = guardian_image

    guardian_rect = displayed_guardian.get_rect(
        topleft=(int(guardian_x), int(guardian_y))
    )

    screen.blit(displayed_guardian, guardian_rect)

    #guardian damage
    if (
        game_started
        and not game_over
        and not victory
        and player.colliderect(guardian_rect)
        and guardian_hit_timer <= 0
    ):

        oxygen = max(0, oxygen - GUARDIAN_DAMAGE)

        guardian_hit_timer = GUARDIAN_HIT_COOLDOWN

        if oxygen <= 0:
            game_over = True


    #draw player
    current_player_image = player_frames[player_direction][player_frame_index]

    player_image_rect = current_player_image.get_rect(
    center=player.center
    )

    screen.blit(current_player_image, player_image_rect) 
    #draw fragment
    if not fragment_collected and not victory:
        draw_artifact(screen, fragment)

    #o2 bar
    bar_width = 200
    bar_height = 18

    pygame.draw.rect(
        screen, (40, 40, 55),
        (20, 20, bar_width, bar_height)
    )

    pygame.draw.rect(
        screen,
        (50, 200, 220),
        (20, 20, int(bar_width * oxygen / MAX_OXYGEN), bar_height)
    )

    pygame.draw.rect(
        screen, (255, 255, 255),
        (20, 20, bar_width, bar_height), 2
    )

    oxygen_text = button_font.render(
        f"OXYGEN: {int(oxygen)}%", True, (255, 255, 255)
    )

    screen.blit(oxygen_text, (20, 45))

    #lvl and fragment counter
    level_text = button_font.render(
        f"LEVEL {level}: {level_names[level - 1]}",
        True, (255, 255, 255)
    )

    screen.blit(level_text, (20, 85))

    fragment_text = button_font.render(
        f"FRAGMENTS: {fragments_collected}/3",
        True, (255, 255, 255)
    )

    screen.blit(fragment_text, (20, 120))

    #lvl transition overlay
    if transitioning:

        fade_surface = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )

        fade_surface.fill(
            (0, 0, 20, int(transition_alpha))
        )

        screen.blit(fade_surface, (0, 0))

        #display next lvl title in fade
        level_text = title_font.render(
            level_names[next_level - 1],
            True,
            (255, 255, 255)
        )

        screen.blit(
            level_text,
            level_text.get_rect(
                center=(WIDTH // 2, HEIGHT // 2)
            )
        )

    #game over screen
    if game_over:

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, 190))
        screen.blit(overlay, (0, 0))

        text = title_font.render(
            "GAME OVER", True, (255, 100, 100)
        )

        screen.blit(
            text,
            text.get_rect(center=(WIDTH // 2, 230))
        )

        subtitle = button_font.render(
            "Your journey has ended.",
            True, (255, 255, 255)
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(center=(WIDTH // 2, 310))
        )

        pygame.draw.rect(
            screen, (30, 120, 150), restart_button
        )

        button_text = button_font.render(
            "TRY AGAIN", True, (255, 255, 255)
        )

        screen.blit(
            button_text,
            button_text.get_rect(center=restart_button.center)
        )

    #victory scteen
    if victory:

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 30, 200))
        screen.blit(overlay, (0, 0))

        text = title_font.render(
            "ARTIFACTS RESTORED!",
            True, (255, 220, 100)
        )

        screen.blit(
            text,
            text.get_rect(center=(WIDTH // 2, 230))
        )

        subtitle = button_font.render(
            "You have restored balance to the underwater world.",
            True, (255, 255, 255)
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(center=(WIDTH // 2, 315))
        )

        pygame.draw.rect(
            screen, (30, 120, 150), restart_button
        )

        button_text = button_font.render(
            "PLAY AGAIN", True, (255, 255, 255)
        )

        screen.blit(
            button_text,
            button_text.get_rect(center=restart_button.center)
        )

    #start screen
    if not game_started:

        screen.fill((0,0,0))
        
        title = title_font.render(
            "ABYSS", True, (100, 220, 240)
        )

        screen.blit(
            title,
            title.get_rect(center=(WIDTH // 2, 170))
        )

        subtitle = button_font.render(
            "A Journey Through The Underworld",
            True, (255, 255, 255)
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(center=(WIDTH // 2, 235))
        )

        story = button_font.render(
            "Recover the three fragments and restore the artifact.",
            True, (220, 220, 220)
        )

        screen.blit(
            story,
            story.get_rect(center=(WIDTH // 2, 290))
        )

        pygame.draw.rect(
            screen, (30, 120, 150), start_button
        )

        button_text = button_font.render(
            "START GAME", True, (255, 255, 255)
        )

        screen.blit(
            button_text,
            button_text.get_rect(center=start_button.center)
        )

    #update display
    pygame.display.flip()

pygame.quit()
