import pygame as pg
import numpy as np

# =========================================================
# SevEngine v1
# Lightweight Mode 7 / pseudo-3D renderer
# =========================================================
#
# Required files:
# - Skybox image (2 samples given in folder)
# - Floor image (2 samples given in folder)
#
# Controls:
# - W / Up Arrow    -> Move forward
# - S / Down Arrow  -> Move backward
# - A / Left Arrow  -> Rotate left
# - D / Right Arrow -> Rotate right
#
# =========================================================


# =========================================================
# SETTINGS
# =========================================================

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

FOV = 60
TEXTURE_SCALE = 30
SHADE_STRENGTH = 0.5

RENDER_WIDTH = 120 # HORIZONTAL RESOLUTION
HALF_RENDER_HEIGHT = 100 # HALF OF VERTICAL RESOLUTION

MOVE_SPEED = 0.005
ROTATION_SPEED = 0.001
FPS_LIMIT = 60

SKYBOX = "assets/skybox.jpg" # CHANGE TO DESIRED FILE
FLOOR = "assets/floor.jpg" # CHANGE TO DESIRED FILE

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


# Convert textures to NumPy arrays
sky = pg.surfarray.array3d(
    pg.transform.scale(
        sky_img,
        (sky_width, HALF_RENDER_HEIGHT * 2)
    )
)

floor = pg.surfarray.array3d(floor_img)


# =========================================================
# MOVEMENT
# =========================================================


def movement(player_x, player_y, rotation, keys, dt):

    # Rotate left
    if keys[pg.K_LEFT] or keys[ord('a')]:
        rotation -= ROTATION_SPEED * dt

    # Rotate right
    if keys[pg.K_RIGHT] or keys[ord('d')]:
        rotation += ROTATION_SPEED * dt

    # Move forward
    if keys[pg.K_UP] or keys[ord('w')]:
        player_x += np.cos(rotation) * MOVE_SPEED * dt
        player_y += np.sin(rotation) * MOVE_SPEED * dt

    # Move backward
    if keys[pg.K_DOWN] or keys[ord('s')]:
        player_x -= np.cos(rotation) * MOVE_SPEED * dt
        player_y -= np.sin(rotation) * MOVE_SPEED * dt

    return player_x, player_y, rotation


# =========================================================
# MAIN LOOP
# =========================================================

while running:

    # -----------------------------------------------------
    # EVENTS
    # -----------------------------------------------------

    for event in pg.event.get():

        if event.type == pg.QUIT:
            running = False


    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    for column in range(RENDER_WIDTH):

        # Current ray angle
        ray_rotation = (
            rotation +
            np.deg2rad(column / projection_scale - 30)
        )

        sin = np.sin(ray_rotation)
        cos = np.cos(ray_rotation)

        # Fisheye correction
        correction = np.cos(
            np.deg2rad(column / projection_scale - 30)
        )


        # -------------------------------------------------
        # SKYBOX
        # -------------------------------------------------

        sky_x = int(
            np.rad2deg(ray_rotation) * sky_width / 120
        ) % sky_width

        frame[column][:] = sky[sky_x][:] / 255


        # -------------------------------------------------
        # FLOOR
        # -------------------------------------------------

        for row in range(HALF_RENDER_HEIGHT):

            # Perspective depth
            depth = (
                HALF_RENDER_HEIGHT /
                (HALF_RENDER_HEIGHT - row)
            ) / correction

            # World coordinates
            world_x = player_x + cos * depth
            world_y = player_y + sin * depth


            # Infinite tiled texture sampling
            texture_x = int(
                (world_x / TEXTURE_SCALE % 1)
                * (floor_width - 1)
            )

            texture_y = int(
                (world_y / TEXTURE_SCALE % 1)
                * (floor_height - 1)
            )


            # Distance shading
            base_shade = (
                0.2 +
                0.8 * (1 - row / HALF_RENDER_HEIGHT)
            )

            shade = (
                1 -
                (1 - base_shade) * SHADE_STRENGTH
            )


            # Draw pixel
            frame[column][
                HALF_RENDER_HEIGHT * 2 - row - 1
            ] = (
                shade * floor[texture_x][texture_y] / 255
            )


    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    surface = pg.surfarray.make_surface(frame * 255)

    # Scale low-resolution render to window size
    surface = pg.transform.scale(
        surface,
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )

    fps = int(clock.get_fps())

    pg.display.set_caption(
        f"SevEngine v1 - FPS: {fps}"
    )

    screen.blit(surface, (0, 0))
    pg.display.update()


    # -----------------------------------------------------
    # UPDATE MOVEMENT
    # -----------------------------------------------------

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