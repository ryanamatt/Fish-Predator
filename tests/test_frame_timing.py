"""
Test to analyze frame timing and identify bottlenecks in the rendering loop.
This simulates the GUI loop to find where time is being wasted.
"""
import time
import numpy as np


def test_pygame_rendering_overhead():
    """Test if pygame rendering is the bottleneck"""
    import pygame
    import boid_engine
    
    WIDTH, HEIGHT = 1200, 800
    BOID_COUNT = 5000
    
    print(f"\n{'='*60}")
    print(f"Pygame Rendering Overhead Test")
    print(f"{'='*60}\n")
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    sim = boid_engine.Simulation(BOID_COUNT, float(WIDTH), float(HEIGHT))
    predator_pos = boid_engine.Vector2D(float(WIDTH/2), float(HEIGHT/2))
    
    # Test components separately
    times = {
        'sim_step': [],
        'get_state': [],
        'numpy_calc': [],
        'render': [],
        'display_flip': [],
        'total': []
    }
    
    COLOR_HEAD = np.array([0, 220, 255], dtype=np.uint8)
    COLOR_TAIL = np.array([0, 100, 150], dtype=np.uint8)
    
    print("Measuring component timings over 60 frames...\n")
    
    for i in range(60):
        frame_start = time.perf_counter()
        
        # 1. Simulation step
        t0 = time.perf_counter()
        sim.step(predator_pos)
        t1 = time.perf_counter()
        times['sim_step'].append((t1 - t0) * 1000)
        
        # 2. Get state
        t0 = time.perf_counter()
        state = sim.get_full_state()
        pos = state[:, :2]
        vel = state[:, 2:]
        t1 = time.perf_counter()
        times['get_state'].append((t1 - t0) * 1000)
        
        # 3. Numpy calculations
        t0 = time.perf_counter()
        v_mag = np.linalg.norm(vel, axis=1, keepdims=True)
        v_mag = np.maximum(v_mag, 1.0)
        dir_vec = vel / v_mag
        head_pos = (pos + dir_vec * 2).astype(np.int32)
        tail_pos = (pos - dir_vec * 3).astype(np.int32)
        body_pos = pos.astype(np.int32)
        t1 = time.perf_counter()
        times['numpy_calc'].append((t1 - t0) * 1000)
        
        # 4. Rendering
        t0 = time.perf_counter()
        screen.fill((15, 15, 20))
        pixels = pygame.surfarray.pixels3d(screen)
        
        def draw_points(coords, color):
            mask = ((coords[:, 0] >= 0) & (coords[:, 0] < WIDTH) & 
                    (coords[:, 1] >= 0) & (coords[:, 1] < HEIGHT))
            valid = coords[mask]
            if len(valid) > 0:
                pixels[valid[:, 0], valid[:, 1]] = color
        
        draw_points(tail_pos, COLOR_TAIL)
        draw_points(body_pos, COLOR_HEAD)
        draw_points(head_pos, COLOR_HEAD)
        del pixels
        t1 = time.perf_counter()
        times['render'].append((t1 - t0) * 1000)
        
        # 5. Display flip
        t0 = time.perf_counter()
        pygame.display.flip()
        t1 = time.perf_counter()
        times['display_flip'].append((t1 - t0) * 1000)
        
        frame_end = time.perf_counter()
        times['total'].append((frame_end - frame_start) * 1000)
    
    pygame.quit()
    
    # Print results
    print(f"{'Component':<20} {'Avg (ms)':<12} {'% of Total':<12} {'Min (ms)':<12} {'Max (ms)'}")
    print(f"{'-'*68}")
    
    total_avg = np.mean(times['total'])
    
    for component in ['sim_step', 'get_state', 'numpy_calc', 'render', 'display_flip', 'total']:
        avg = np.mean(times[component])
        min_val = np.min(times[component])
        max_val = np.max(times[component])
        pct = (avg / total_avg * 100) if component != 'total' else 100.0
        
        print(f"{component:<20} {avg:>8.2f}    {pct:>8.1f}%    {min_val:>8.2f}    {max_val:>8.2f}")
    
    print(f"\n{'='*68}")
    print(f"Theoretical max FPS: {1000/total_avg:.1f}")
    print(f"Target FPS (60): {'ACHIEVABLE' if total_avg < 16.67 else 'NOT ACHIEVABLE'}")
    
    # Identify bottleneck
    component_avgs = {k: np.mean(v) for k, v in times.items() if k != 'total'}
    bottleneck = max(component_avgs.items(), key=lambda x: x[1])
    print(f"Primary bottleneck: {bottleneck[0]} ({bottleneck[1]:.2f} ms)")


def test_frame_rate_with_sleep():
    """Test different sleep strategies to see CPU impact"""
    import pygame
    import boid_engine
    
    WIDTH, HEIGHT = 1200, 800
    BOID_COUNT = 5000
    
    print(f"\n{'='*60}")
    print(f"Frame Rate Sleep Strategy Test")
    print(f"{'='*60}\n")
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    sim = boid_engine.Simulation(BOID_COUNT, float(WIDTH), float(HEIGHT))
    predator_pos = boid_engine.Vector2D(float(WIDTH/2), float(HEIGHT/2))
    
    strategies = {
        'clock.tick(60)': lambda frame_time: clock.tick(60),
        'time.sleep(fixed)': lambda frame_time: time.sleep(1.0/60.0) or clock.tick(),
        'time.sleep(adaptive)': lambda frame_time: (time.sleep(max(0, 1.0/60.0 - frame_time)) or clock.tick()),
        'no_sleep': lambda frame_time: clock.tick(),
    }
    
    import psutil
    import os
    process = psutil.Process(os.getpid())
    
    for strategy_name, strategy_func in strategies.items():
        print(f"\nTesting: {strategy_name}")
        
        # Warmup
        for _ in range(10):
            sim.step(predator_pos)
            screen.fill((0, 0, 0))
            pygame.display.flip()
        
        cpu_samples = []
        fps_samples = []
        
        for i in range(100):
            frame_start = time.perf_counter()
            
            sim.step(predator_pos)
            screen.fill((0, 0, 0))
            pygame.display.flip()
            
            frame_time = time.perf_counter() - frame_start
            strategy_func(frame_time)
            
            if i % 10 == 0:
                cpu_samples.append(process.cpu_percent())
                fps_samples.append(clock.get_fps())
        
        avg_cpu = np.mean(cpu_samples)
        avg_fps = np.mean(fps_samples)
        
        print(f"  Average CPU: {avg_cpu:.1f}%")
        print(f"  Average FPS: {avg_fps:.1f}")
    
    pygame.quit()


if __name__ == "__main__":
    import sys
    
    try:
        import pygame
        import boid_engine
        import psutil
    except ImportError as e:
        print(f"ERROR: Missing required module: {e}")
        print("Install with: pip install pygame psutil")
        sys.exit(1)
    
    test_pygame_rendering_overhead()
    test_frame_rate_with_sleep()