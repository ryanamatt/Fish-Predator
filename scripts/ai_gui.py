import pygame
import numpy as np
import os
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OMP_WAIT_POLICY'] = 'PASSIVE'
import boid_engine

WIDTH, HEIGHT = 1200, 800
BOID_COUNT = 1000

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

# AI Predator state
class AIPredator:
    def __init__(self):
        self.pos = np.array([WIDTH / 2, HEIGHT / 2], dtype=float)
        self.vel = np.array([0.0, 0.0], dtype=float)
        self.max_speed = 3.5
        self.max_force = 0.2
        self.hunt_radius = 200.0  # Distance to look for prey
        self.eat_radius = 20.0  # Distance to catch and eat a boid
        self.wander_angle = 0.0
        self.boids_eaten = 0
        
    def seek(self, target):
        """Steer toward a target"""
        desired = target - self.pos
        dist = np.linalg.norm(desired)
        if dist > 0:
            desired = (desired / dist) * self.max_speed
            steer = desired - self.vel
            steer_mag = np.linalg.norm(steer)
            if steer_mag > self.max_force:
                steer = (steer / steer_mag) * self.max_force
            return steer
        return np.array([0.0, 0.0])
    
    def wander(self):
        """Random wandering behavior"""
        self.wander_angle += (np.random.random() - 0.5) * 0.5
        
        # Project circle in front of predator
        circle_center = self.vel.copy()
        if np.linalg.norm(circle_center) > 0:
            circle_center = (circle_center / np.linalg.norm(circle_center)) * 4.0
        
        # Random point on circle
        displacement = np.array([
            2.0 * np.cos(self.wander_angle),
            2.0 * np.sin(self.wander_angle)
        ])
        
        wander_force = circle_center + displacement
        wander_mag = np.linalg.norm(wander_force)
        if wander_mag > self.max_force:
            wander_force = (wander_force / wander_mag) * self.max_force
        
        return wander_force
    
    def hunt(self, boid_positions):
        """Main AI behavior - hunt the flock. Returns indices of boids to eat."""
        if len(boid_positions) == 0:
            return []
        
        # Find nearest boid
        distances = np.linalg.norm(boid_positions - self.pos, axis=1)
        nearest_idx = np.argmin(distances)
        nearest_dist = distances[nearest_idx]
        
        # Check if we can eat any boids
        boids_to_eat = []
        eat_mask = distances < self.eat_radius
        if np.any(eat_mask):
            boids_to_eat = np.where(eat_mask)[0].tolist()
            self.boids_eaten += len(boids_to_eat)
        
        # Strategy: hunt nearby boids, otherwise move to flock center
        if nearest_dist < self.hunt_radius:
            # Hunt the nearest boid
            target = boid_positions[nearest_idx]
            hunt_force = self.seek(target)
            self.vel += hunt_force * 2.0  # Strong hunting force
        else:
            # Move toward center of flock
            flock_center = np.mean(boid_positions, axis=0)
            center_force = self.seek(flock_center)
            self.vel += center_force * 1.0
        
        # Add wandering for natural movement
        wander_force = self.wander()
        self.vel += wander_force * 0.5
        
        # Limit velocity
        vel_mag = np.linalg.norm(self.vel)
        if vel_mag > self.max_speed:
            self.vel = (self.vel / vel_mag) * self.max_speed
        
        # Update position
        self.pos += self.vel
        
        # Wrap around world boundaries
        self.pos[0] = self.pos[0] % WIDTH
        self.pos[1] = self.pos[1] % HEIGHT
        
        return boids_to_eat

predator = AIPredator()

running = True
frame_count = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False

    state = sim.get_full_state()
    boid_positions = state[:, :2]
    
    boids_to_eat = predator.hunt(boid_positions)
    
    # Remove eaten boids from the simulation
    if len(boids_to_eat) > 0:
        sim.remove_boids(boids_to_eat)
    
    predator_pos = boid_engine.Vector2D(float(predator.pos[0]), float(predator.pos[1]))
    
    for _ in range(PHYSICS_STEPS_PER_RENDER):
        sim.step(predator_pos)
    
    frame_count += 1
    
    if frame_count % RENDER_EVERY_N_FRAMES != 0:
        clock.tick(60)
        continue

    state = sim.get_full_state()
    pos = state[:, :2]
    vel = state[:, 2:]

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

    predator_x, predator_y = int(predator.pos[0]), int(predator.pos[1])
    
    # Draw predator as a red circle with velocity indicator
    pygame.draw.circle(screen, (255, 50, 50), (predator_x, predator_y), 15, 2)
    pygame.draw.circle(screen, (255, 100, 100), (predator_x, predator_y), 8, 0)
    
    # Draw velocity vector
    vel_indicator = predator.vel * 5
    end_pos = (int(predator_x + vel_indicator[0]), int(predator_y + vel_indicator[1]))
    pygame.draw.line(screen, (255, 150, 150), (predator_x, predator_y), end_pos, 2)
    
    # Update display
    current_boid_count = len(sim.boids)
    pygame.display.set_caption(
        f"Boids: {current_boid_count} | Eaten: {predator.boids_eaten} | FPS: {int(clock.get_fps())} | AI Predator"
    )
    pygame.display.flip()
    clock.tick(60)

pygame.quit()