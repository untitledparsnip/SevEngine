import pygame as pg
import numpy as np
from numba import njit

# =========================================================
# SevEngine v1.1 Numba
# Numba Optimized
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

RENDER_WIDTH = 240
HALF_RENDER_HEIGHT = 200

MOVE_SPEED = 0.005
ROTATION_SPEED = 0.001

FPS_LIMIT = 60

SKYBOX = "assets/skybox.jpg"
FLOOR = "assets/floor.jpg"

# =========================================================
# WORLD SETTINGS
# =========================================================

INFINITE_WORLD = False

BORDER_SIZE = 2048
BORDER_COLOR = (0, 0, 0)

# =========================================================
# INITIALIZE
# =========================================================

pg.init()

screen = pg.display.set_mode(
    (WINDOW_WIDTH, WINDOW_HEIGHT)
)

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

# IMPORTANT:
# uint8 framebuffer for pygame compatibility
frame = np.zeros(
    (
        RENDER_WIDTH,
        HALF_RENDER_HEIGHT * 2,
        3
    ),
    dtype=np.uint8
)

# =========================================================
# LOAD TEXTURES
# =========================================================

sky_img = pg.image.load(SKYBOX).convert()
floor_img = pg.image.load(FLOOR).convert()

sky_width, sky_height = sky_img.get_size()
floor_width, floor_height = floor_img.get_size()

# SKY
sky = pg.surfarray.array3d(
    pg.transform.scale(
        sky_img,
        (
            sky_width,
            HALF_RENDER_HEIGHT * 2
        )
    )
)

# FLOOR
floor = pg.surfarray.array3d(floor_img)

# =========================================================
# FINITE WORLD CONSTRUCTION
# =========================================================

finite_width = floor_width + BORDER_SIZE * 2
finite_height = floor_height + BORDER_SIZE * 2

finite_surface = pg.Surface(
    (
        finite_width,
        finite_height
    )
)

finite_surface.fill(BORDER_COLOR)

finite_surface.blit(
    floor_img,
    (
        BORDER_SIZE,
        BORDER_SIZE
    )
)

finite_floor = pg.surfarray.array3d(
    finite_surface
)

# =========================================================
# MOVEMENT
# =========================================================

def movement(
    player_x,
    player_y,
    rotation,
    keys,
    dt
):

    # Rotate left
    if keys[pg.K_LEFT] or keys[ord('a')]:
        rotation -= ROTATION_SPEED * dt

    # Rotate right
    if keys[pg.K_RIGHT] or keys[ord('d')]:
        rotation += ROTATION_SPEED * dt

    # Forward
    if keys[pg.K_UP] or keys[ord('w')]:
        player_x += np.cos(rotation) * MOVE_SPEED * dt
        player_y += np.sin(rotation) * MOVE_SPEED * dt

    # Backward
    if keys[pg.K_DOWN] or keys[ord('s')]:
        player_x -= np.cos(rotation) * MOVE_SPEED * dt
        player_y -= np.sin(rotation) * MOVE_SPEED * dt

    return player_x, player_y, rotation

# =========================================================
# NUMBA FLOOR RENDERER
# =========================================================

@njit(fastmath=True)
def render_floor(
    frame,
    column,
    tex,
    tex_w,
    tex_h,
    player_x,
    player_y,
    cos,
    sin,
    correction,
    half_h,
    texture_scale,
    infinite_world,
    border_size,
    finite_w,
    finite_h,
    shade_strength
):

    for row in range(half_h):

        # Perspective depth
        depth = (
            half_h /
            (half_h - row)
        ) / correction

        # World coordinates
        world_x = player_x + cos * depth
        world_y = player_y + sin * depth

        # =================================================
        # INFINITE WORLD
        # =================================================

        if infinite_world:

            tx = int(
                (
                    (world_x / texture_scale)
                    % 1.0
                ) * (tex_w - 1)
            )

            ty = int(
                (
                    (world_y / texture_scale)
                    % 1.0
                ) * (tex_h - 1)
            )

        # =================================================
        # FINITE WORLD
        # =================================================

        else:

            tx = int(
                world_x * texture_scale
                + border_size
            )

            ty = int(
                world_y * texture_scale
                + border_size
            )

            # Clamp
            if tx < 0:
                tx = 0

            elif tx >= finite_w:
                tx = finite_w - 1

            if ty < 0:
                ty = 0

            elif ty >= finite_h:
                ty = finite_h - 1

        # =================================================
        # SHADING
        # =================================================

        base_shade = (
            0.2 +
            0.8 * (
                1.0 -
                row / half_h
            )
        )

        shade = (
            1.0 -
            (
                1.0 -
                base_shade
            ) * shade_strength
        )

        # Screen Y position
        screen_y = (
            half_h * 2 -
            row - 1
        )

        # =================================================
        # DRAW PIXEL
        # =================================================

        frame[column, screen_y, 0] = int(
            shade * tex[tx, ty, 0]
        )

        frame[column, screen_y, 1] = int(
            shade * tex[tx, ty, 1]
        )

        frame[column, screen_y, 2] = int(
            shade * tex[tx, ty, 2]
        )

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

    # =====================================================
    # RENDER
    # =====================================================

    for column in range(RENDER_WIDTH):

        # Current ray angle
        ray_rotation = (
            rotation +
            np.deg2rad(
                column /
                projection_scale
                - 30
            )
        )

        cos = np.cos(ray_rotation)
        sin = np.sin(ray_rotation)

        # Fisheye correction
        correction = np.cos(
            np.deg2rad(
                column /
                projection_scale
                - 30
            )
        )

        # =================================================
        # SKY
        # =================================================

        sky_x = int(
            np.rad2deg(ray_rotation)
            * sky_width
            / 120
        ) % sky_width

        frame[column][:] = sky[sky_x]

        # =================================================
        # FLOOR
        # =================================================

        render_floor(
            frame,
            column,
            floor if INFINITE_WORLD else finite_floor,
            floor_width,
            floor_height,
            player_x,
            player_y,
            cos,
            sin,
            correction,
            HALF_RENDER_HEIGHT,
            TEXTURE_SCALE,
            INFINITE_WORLD,
            BORDER_SIZE,
            finite_width,
            finite_height,
            SHADE_STRENGTH
        )

    # =====================================================
    # DISPLAY
    # =====================================================

    surface = pg.surfarray.make_surface(
        frame
    )

    surface = pg.transform.scale(
        surface,
        (
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )
    )

    pg.display.set_caption(
        f"SevEngine v1.1 | "
        f"{'INFINITE' if INFINITE_WORLD else 'FINITE'} | "
        f"FPS {int(clock.get_fps())}"
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