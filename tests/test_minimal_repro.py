"""
Minimal reproduction test - tests the exact issue from gui.py
This simulates the actual GUI loop to identify the specific CPU issue.
"""
import time
import psutil
import os


def test_clock_tick_cpu_usage():
    """Test if pygame's clock.tick() is the culprit"""
    import pygame
    
    print(f"\n{'='*60}")
    print(f"Clock.tick() CPU Usage Test")
    print(f"{'='*60}\n")
    
    pygame.init()
    clock = pygame.time.Clock()
    
    process = psutil.Process(os.getpid())
    
    print("Testing clock.tick(60) for 5 seconds...")
    print("(This is the ORIGINAL code from gui.py)\n")
    
    # Original method: clock.tick(60)
    cpu_samples = []
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < 5:
        # Minimal work (no simulation)
        if frame_count % 10 == 0:
            cpu_samples.append(process.cpu_percent())
        
        clock.tick(60)  # THIS IS THE PROBLEM
        frame_count += 1
    
    avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
    print(f"Method: clock.tick(60)")
    print(f"  Frames: {frame_count}")
    print(f"  Average CPU: {avg_cpu:.1f}%")
    print(f"  FPS: {frame_count / 5:.1f}")
    
    if avg_cpu > 5:
        print(f"  ⚠ HIGH CPU! clock.tick() is busy-waiting!")
    
    # New method: time.sleep()
    print(f"\n{'-'*60}\n")
    print("Testing time.sleep() for 5 seconds...")
    print("(This is the FIXED code)\n")
    
    cpu_samples = []
    start_time = time.time()
    frame_count = 0
    target_frame_time = 1.0 / 60.0
    
    while time.time() - start_time < 5:
        frame_start = time.perf_counter()
        
        # Minimal work (no simulation)
        if frame_count % 10 == 0:
            cpu_samples.append(process.cpu_percent())
        
        # NEW METHOD: time.sleep() instead of clock.tick()
        frame_time = time.perf_counter() - frame_start
        sleep_time = target_frame_time - frame_time
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        clock.tick()  # Just for FPS measurement
        frame_count += 1
    
    avg_cpu_new = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
    print(f"Method: time.sleep()")
    print(f"  Frames: {frame_count}")
    print(f"  Average CPU: {avg_cpu_new:.1f}%")
    print(f"  FPS: {frame_count / 5:.1f}")
    
    if avg_cpu_new < 5:
        print(f"  ✓ LOW CPU! time.sleep() yields the CPU properly!")
    
    # Compare
    print(f"\n{'='*60}")
    print(f"COMPARISON")
    print(f"{'='*60}")
    print(f"clock.tick(60):  {avg_cpu:.1f}% CPU")
    print(f"time.sleep():    {avg_cpu_new:.1f}% CPU")
    print(f"Improvement:     {avg_cpu - avg_cpu_new:.1f}% reduction")
    
    pygame.quit()


def test_with_actual_simulation():
    """Test CPU usage with the actual boid simulation"""
    import pygame
    import boid_engine
    import numpy as np
    
    print(f"\n{'='*60}")
    print(f"Full Simulation CPU Test")
    print(f"{'='*60}\n")
    
    WIDTH, HEIGHT = 1200, 800
    BOID_COUNT = 5000
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    sim = boid_engine.Simulation(BOID_COUNT, float(WIDTH), float(HEIGHT))
    predator_pos = boid_engine.Vector2D(float(WIDTH/2), float(HEIGHT/2))
    
    process = psutil.Process(os.getpid())
    
    # Test OLD way (clock.tick)
    print("Testing OLD method (clock.tick) for 3 seconds...")
    
    cpu_samples = []
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < 3:
        # Full simulation + rendering
        sim.step(predator_pos)
        state = sim.get_full_state()
        
        screen.fill((15, 15, 20))
        # (skip actual rendering to focus on CPU)
        pygame.display.flip()
        
        if frame_count % 10 == 0:
            cpu_samples.append(process.cpu_percent())
        
        clock.tick(60)  # OLD METHOD
        frame_count += 1
    
    old_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
    old_fps = frame_count / 3
    
    print(f"  CPU: {old_cpu:.1f}%")
    print(f"  FPS: {old_fps:.1f}")
    
    # Test NEW way (time.sleep)
    print(f"\nTesting NEW method (time.sleep) for 3 seconds...")
    
    cpu_samples = []
    start_time = time.time()
    frame_count = 0
    target_frame_time = 1.0 / 60.0
    
    while time.time() - start_time < 3:
        frame_start = time.perf_counter()
        
        # Full simulation + rendering
        sim.step(predator_pos)
        state = sim.get_full_state()
        
        screen.fill((15, 15, 20))
        pygame.display.flip()
        
        if frame_count % 10 == 0:
            cpu_samples.append(process.cpu_percent())
        
        # NEW METHOD
        frame_time = time.perf_counter() - frame_start
        sleep_time = target_frame_time - frame_time
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        clock.tick()
        frame_count += 1
    
    new_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
    new_fps = frame_count / 3
    
    print(f"  CPU: {new_cpu:.1f}%")
    print(f"  FPS: {new_fps:.1f}")
    
    # Results
    print(f"\n{'='*60}")
    print(f"VERDICT")
    print(f"{'='*60}")
    
    improvement = old_cpu - new_cpu
    improvement_pct = (improvement / old_cpu * 100) if old_cpu > 0 else 0
    
    print(f"OLD (clock.tick):  {old_cpu:.1f}% CPU @ {old_fps:.1f} FPS")
    print(f"NEW (time.sleep):  {new_cpu:.1f}% CPU @ {new_fps:.1f} FPS")
    print(f"\nCPU Reduction: {improvement:.1f}% ({improvement_pct:.0f}% improvement)")
    
    if improvement > 20:
        print(f"\n✓ CONFIRMED: clock.tick() was causing excessive CPU usage!")
        print(f"  The fix in gui.py should resolve the issue.")
    elif improvement < 5:
        print(f"\n⚠ WARNING: clock.tick() is not the main issue.")
        print(f"  Check other test results for the real bottleneck.")
    else:
        print(f"\n✓ clock.tick() contributed to CPU usage, but there may be other issues.")
    
    pygame.quit()


if __name__ == "__main__":
    import sys
    
    try:
        import pygame
        import psutil
    except ImportError as e:
        print(f"ERROR: {e}")
        print("Install with: pip install pygame psutil")
        sys.exit(1)
    
    # Run both tests
    test_clock_tick_cpu_usage()
    
    try:
        import boid_engine
        test_with_actual_simulation()
    except ImportError:
        print("\n" + "="*60)
        print("Skipping full simulation test (boid_engine not built)")
        print("Build with: pip install .")
        print("="*60)