"""
Test to measure actual CPU usage of the boid simulation.
This will help identify where CPU cycles are being wasted.
"""
import psutil
import time
import os
import sys

def test_cpu_usage_during_simulation():
    """Measure CPU usage while running the simulation"""
    import boid_engine
    
    WIDTH, HEIGHT = 1200, 800
    BOID_COUNT = 5000
    
    print(f"\n{'='*60}")
    print(f"CPU Usage Test - {BOID_COUNT} boids")
    print(f"{'='*60}\n")
    
    # Get the current process
    process = psutil.Process(os.getpid())
    
    # Create simulation
    sim = boid_engine.Simulation(BOID_COUNT, float(WIDTH), float(HEIGHT))
    predator_pos = boid_engine.Vector2D(float(WIDTH/2), float(HEIGHT/2))
    
    # Warmup
    print("Warming up...")
    for _ in range(10):
        sim.step(predator_pos)
    
    # Measure CPU usage during simulation
    print("\nMeasuring CPU usage over 100 frames...")
    cpu_percentages = []
    frame_times = []
    
    for i in range(100):
        cpu_before = process.cpu_percent()
        
        start = time.perf_counter()
        sim.step(predator_pos)
        end = time.perf_counter()
        
        cpu_after = process.cpu_percent()
        
        frame_times.append((end - start) * 1000)  # ms
        cpu_percentages.append(cpu_after)
        
        time.sleep(0.001)  # Small delay to let CPU measurement settle
    
    avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
    avg_frame_time = sum(frame_times) / len(frame_times)
    
    print(f"\nResults:")
    print(f"  Average CPU usage: {avg_cpu:.1f}%")
    print(f"  Average frame time: {avg_frame_time:.2f} ms")
    print(f"  Theoretical max FPS: {1000/avg_frame_time:.1f}")
    print(f"  CPU cores available: {psutil.cpu_count()}")
    print(f"  Expected CPU usage (single thread): {100/psutil.cpu_count():.1f}%")
    
    # Check if OpenMP is utilizing multiple cores
    if avg_cpu > 150:
        print(f"\n  ✓ Multi-threading is working (using ~{avg_cpu/100:.1f} cores)")
    else:
        print(f"\n  ⚠ Multi-threading may not be working efficiently")
    
    return avg_cpu, avg_frame_time


def test_idle_cpu_usage():
    """Test CPU usage when simulation is created but not stepped"""
    import boid_engine
    
    print(f"\n{'='*60}")
    print(f"Idle CPU Usage Test")
    print(f"{'='*60}\n")
    
    process = psutil.Process(os.getpid())
    
    # Baseline CPU
    baseline_samples = []
    for _ in range(5):
        baseline_samples.append(process.cpu_percent())
        time.sleep(0.1)
    
    baseline_cpu = sum(baseline_samples) / len(baseline_samples)
    print(f"Baseline CPU (no simulation): {baseline_cpu:.1f}%")
    
    # Create simulation but don't step it
    sim = boid_engine.Simulation(5000, 1200.0, 800.0)
    
    idle_samples = []
    for _ in range(5):
        idle_samples.append(process.cpu_percent())
        time.sleep(0.1)
    
    idle_cpu = sum(idle_samples) / len(idle_samples)
    print(f"CPU after creating simulation (idle): {idle_cpu:.1f}%")
    
    if idle_cpu > baseline_cpu + 5:
        print(f"  ⚠ WARNING: Simulation using CPU while idle!")
        print(f"  Difference: +{idle_cpu - baseline_cpu:.1f}%")
        return False
    else:
        print(f"  ✓ Simulation is idle as expected")
        return True


if __name__ == "__main__":
    # Check if boid_engine is available
    try:
        import boid_engine
    except ImportError:
        print("ERROR: boid_engine module not found!")
        print("Please build the module first with: pip install .")
        sys.exit(1)
    
    # Run tests
    idle_ok = test_idle_cpu_usage()
    cpu_usage, frame_time = test_cpu_usage_during_simulation()
    
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"Idle test: {'PASS' if idle_ok else 'FAIL'}")
    print(f"Average CPU: {cpu_usage:.1f}%")
    print(f"Average frame time: {frame_time:.2f} ms")