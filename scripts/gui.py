import pygame
import numpy as np
import os
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OMP_WAIT_POLICY'] = 'PASSIVE'
import boid_engine

WIDTH, HEIGHT = 1200, 800
BOID_COUNT = 5000

# Performance settings
RENDER_EVERY_N_FRAMES = 1  # Set to 2 or 3 to reduce rendering load
PHYSICS_STEPS_PER_RENDER = 1  # Increase to prioritize simulation over visuals

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

sim = boid_engine.Simulation(BOID_COUNT, float(WIDTH), float(HEIGHT))

# Pre-allocate color arrays (avoid repeated array creation)
COLOR_HEAD = np.array([0, 220, 255], dtype=np.uint8)
COLOR_TAIL = np.array([0, 100, 150], dtype=np.uint8)

running = True
frame_count = 0

mx, my = -1000.0, -1000.0
mouse_started = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_started = True
            mx, my = event.pos

    # Get mouse position once
    predator_pos = boid_engine.Vector2D(float(mx), float(my))
    
    # Run physics (potentially multiple steps)
    for _ in range(PHYSICS_STEPS_PER_RENDER):
        sim.step(predator_pos)
    
    frame_count += 1
    
    # Skip rendering on some frames to reduce CPU load
    if frame_count % RENDER_EVERY_N_FRAMES != 0:
        clock.tick(60)
        continue

    # Extract state only when rendering
    state = sim.get_full_state()
    pos = state[:, :2]
    vel = state[:, 2:]

    # Vectorized direction calculation
    v_mag = np.linalg.norm(vel, axis=1, keepdims=True)
    v_mag = np.maximum(v_mag, 1.0)  # Avoid division by zero (faster than boolean indexing)
    dir_vec = vel / v_mag
    
    # Calculate fish positions
    head_pos = (pos + dir_vec * 2).astype(np.int32)
    tail_pos = (pos - dir_vec * 3).astype(np.int32)
    body_pos = pos.astype(np.int32)

    # Clear screen
    screen.fill((15, 15, 20))
    pixels = pygame.surfarray.pixels3d(screen)

    # Optimized bounds checking and drawing
    def draw_points(coords, color):
        # Single vectorized mask operation
        mask = ((coords[:, 0] >= 0) & (coords[:, 0] < WIDTH) & 
                (coords[:, 1] >= 0) & (coords[:, 1] < HEIGHT))
        valid = coords[mask]
        if len(valid) > 0:  # Only draw if there are valid points
            pixels[valid[:, 0], valid[:, 1]] = color

    # Draw layers
    draw_points(tail_pos, COLOR_TAIL)
    draw_points(body_pos, COLOR_HEAD)
    draw_points(head_pos, COLOR_HEAD)

    del pixels  # Unlock surface

    # Draw predator cursor
    if mouse_started:
        pygame.draw.circle(screen, (255, 50, 50), (mx, my), 15, 1)
    
    # Update display
    pygame.display.set_caption(f"Boids: {BOID_COUNT} | FPS: {int(clock.get_fps())}")
    pygame.display.flip()
    clock.tick(60)

pygame.quit()