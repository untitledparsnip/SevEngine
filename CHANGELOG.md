# Changelog

All notable changes to SevEngine will be documented here.

---

# SevEngine v1.1

Release Type:
Major Feature Update

---

## Added

### Finite World Mode
Added optional finite world rendering mode.

Instead of endlessly repeating textures, worlds can now be surrounded by configurable borders.

---

### Infinite / Finite Toggle

Added runtime-configurable world mode:

```python
INFINITE_WORLD = True
```

or

```python
INFINITE_WORLD = False
```

---

### Procedural Border Generation

Finite worlds are generated automatically at runtime.

Features:
- configurable border color
- no manual image editing required

---

### Border Color Customization

Added customizable RGB border coloring.

Example:

```python
BORDER_COLOR = (0, 0, 0)
```

---

### Numba Optimized Build

Added:
- `main_numba.py`

Includes:
- JIT compiled floor rendering
- improved rendering performance
- optimized framebuffer handling

---

## Changed

### Improved Framebuffer Structure
Optimized framebuffer usage for better compatibility with Numba and Pygame.

---

### Improved Finite World Alignment
Fixed player spawning and world offset issues present during early v1.1 development.

---

### Cleaner World Handling
Separated infinite tiling behavior from finite world sampling logic.

---

## Performance

### Standard Version
- stable software rendering
- lightweight architecture
- low dependency count

### Numba Version
- significantly faster floor rendering
- higher usable render resolutions
- smoother framerates on larger scenes

---

## Known Issues

### Finite World Collision
No border collision system yet.

Players can still move into border areas in finite mode.

Planned for v1.2.

---

### Surface Scaling Bottleneck
Current performance is still partially limited by:
- `pygame.surfarray.make_surface`
- `pygame.transform.scale`

Future versions may replace this with lower-overhead rendering paths.

---

# Previous Versions

## v1.0

Initial release.

Features:
- infinite Mode 7 floor rendering
- skybox projection
- distance shading
- movement system
- configurable rendering resolution
