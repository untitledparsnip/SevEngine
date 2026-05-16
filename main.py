import pygame as pg
import numpy as np

# =========================================================
# SevEngine v1.1
# Finite + Infinite Mode Toggle
# =========================================================

# =========================================================
# SETTINGS
# =========================================================

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

FOV = 60
TEXTURE_SCALE = 30
SHADE_STRENGTH = 0.5

RENDER_WIDTH = 120
HALF_RENDER_HEIGHT = 100

MOVE_SPEED = 0.005
ROTATION_SPEED = 0.001

FPS_LIMIT = 60

SKYBOX = "assets/skybox.jpg"
FLOOR = "assets/floor.jpg"

# =========================================================
# WORLD SETTINGS
# =========================================================

INFINITE_WORLD = False

# Border color (RGB)
BORDER_COLOR = (0, 0, 0)

# =========================================================
# INITIALIZE
# =========================================================

pg.init()

screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pg.time.Clock()
running = True


# =========================================================
# PLAYER
# =========================================================

player_x = 0
player_y = 0
rotation = 0


# =========================================================
# RENDER SETUP
# =========================================================

projection_scale = RENDER_WIDTH / FOV

frame = np.random.uniform(
    0,
    1,
    (RENDER_WIDTH, HALF_RENDER_HEIGHT * 2, 3)
)


# =========================================================
# LOAD TEXTURES
# =========================================================

sky_img = pg.image.load(SKYBOX).convert()
floor_img = pg.image.load(FLOOR).convert()

sky_width, sky_height = sky_img.get_size()
floor_width, floor_height = floor_img.get_size()

sky = pg.surfarray.array3d(
    pg.transform.scale(
        sky_img,
        (sky_width, HALF_RENDER_HEIGHT * 2)
    )
)

floor = pg.surfarray.array3d(floor_img)


# =========================================================
# FINITE WORLD CONSTRUCTION
# =========================================================

finite_width = floor_width + BORDER_SIZE * 2
finite_height = floor_height + BORDER_SIZE * 2

finite_surface = pg.Surface((finite_width, finite_height))

finite_surface.fill(BORDER_COLOR)

BORDER_SIZE = 1
finite_surface.blit(floor_img, (BORDER_SIZE, BORDER_SIZE))

finite_floor = pg.surfarray.array3d(finite_surface)


# =========================================================
# MOVEMENT
# =========================================================

def movement(player_x, player_y, rotation, keys, dt):

    if keys[pg.K_LEFT] or keys[ord('a')]:
        rotation -= ROTATION_SPEED * dt

    if keys[pg.K_RIGHT] or keys[ord('d')]:
        rotation += ROTATION_SPEED * dt

    if keys[pg.K_UP] or keys[ord('w')]:
        player_x += np.cos(rotation) * MOVE_SPEED * dt
        player_y += np.sin(rotation) * MOVE_SPEED * dt

    if keys[pg.K_DOWN] or keys[ord('s')]:
        player_x -= np.cos(rotation) * MOVE_SPEED * dt
        player_y -= np.sin(rotation) * MOVE_SPEED * dt

    return player_x, player_y, rotation


# =========================================================
# MAIN LOOP
# =========================================================

while running:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # =====================================================
    # RENDER
    # =====================================================

    for column in range(RENDER_WIDTH):

        ray_rotation = (
            rotation +
            np.deg2rad(column / projection_scale - 30)
        )

        cos = np.cos(ray_rotation)
        sin = np.sin(ray_rotation)

        correction = np.cos(
            np.deg2rad(column / projection_scale - 30)
        )

        # SKY
        sky_x = int(
            np.rad2deg(ray_rotation) * sky_width / 120
        ) % sky_width

        frame[column][:] = sky[sky_x][:] / 255


        # FLOOR
        for row in range(HALF_RENDER_HEIGHT):

            depth = (
                HALF_RENDER_HEIGHT /
                (HALF_RENDER_HEIGHT - row)
            ) / correction

            world_x = player_x + cos * depth
            world_y = player_y + sin * depth


            if INFINITE_WORLD:
                tx = int((world_x / TEXTURE_SCALE) % 1 * (floor_width - 1))
                ty = int((world_y / TEXTURE_SCALE) % 1 * (floor_height - 1))
                tex = floor

            else:
                tx = int(world_x * TEXTURE_SCALE + BORDER_SIZE)
                ty = int(world_y * TEXTURE_SCALE + BORDER_SIZE)

                tx = max(0, min(finite_width - 1, tx))
                ty = max(0, min(finite_height - 1, ty))

                tex = finite_floor


            base_shade = (
                0.2 +
                0.8 * (1 - row / HALF_RENDER_HEIGHT)
            )

            shade = (
                1 -
                (1 - base_shade) * SHADE_STRENGTH
            )


            frame[column][
                HALF_RENDER_HEIGHT * 2 - row - 1
            ] = (
                shade * tex[tx][ty] / 255
            )


    # =====================================================
    # DISPLAY
    # =====================================================

    surface = pg.surfarray.make_surface(frame * 255)

    surface = pg.transform.scale(
        surface,
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )

    pg.display.set_caption(
        f"SevEngine v1.1 | {'INFINITE' if INFINITE_WORLD else 'FINITE'} | FPS {int(clock.get_fps())}"
    )

    screen.blit(surface, (0, 0))
    pg.display.update()


    # =====================================================
    # UPDATE
    # =====================================================

    dt = clock.tick(FPS_LIMIT)

    player_x, player_y, rotation = movement(
        player_x,
        player_y,
        rotation,
        pg.key.get_pressed(),
        dt
    )


# =========================================================
# CLEANUP
# =========================================================

pg.quit()
