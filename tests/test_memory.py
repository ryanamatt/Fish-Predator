"""
Test memory allocations and cache efficiency.
Excessive allocations or poor cache usage can cause high CPU.
"""
import time
import sys
import gc


def test_memory_allocations():
    """Check if the simulation is causing excessive memory allocations"""
    import boid_engine
    import tracemalloc
    
    print(f"\n{'='*60}")
    print(f"Memory Allocation Test")
    print(f"{'='*60}\n")
    
    BOID_COUNT = 5000
    sim = boid_engine.Simulation(BOID_COUNT, 1200.0, 800.0)
    predator_pos = boid_engine.Vector2D(600.0, 400.0)
    
    # Start tracing
    tracemalloc.start()
    
    # Warmup
    for _ in range(10):
        sim.step(predator_pos)
    
    # Clear snapshot
    tracemalloc.clear_traces()
    gc.collect()
    
    # Take snapshot before
    snapshot1 = tracemalloc.take_snapshot()
    
    # Run simulation
    for _ in range(100):
        sim.step(predator_pos)
    
    # Take snapshot after
    snapshot2 = tracemalloc.take_snapshot()
    
    # Compare
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    print("Top 10 memory allocations during simulation:\n")
    for stat in top_stats[:10]:
        print(f"{stat}")
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"\nCurrent memory: {current / 1024:.1f} KB")
    print(f"Peak memory: {peak / 1024:.1f} KB")
    
    tracemalloc.stop()
    
    if peak > 50 * 1024 * 1024:  # 50 MB
        print("\n⚠ WARNING: High memory allocations detected during simulation")
    else:
        print("\n✓ Memory usage looks reasonable")


def test_get_full_state_overhead():
    """Test if get_full_state() is causing allocations or copies"""
    import boid_engine
    import numpy as np
    
    print(f"\n{'='*60}")
    print(f"get_full_state() Overhead Test")
    print(f"{'='*60}\n")
    
    BOID_COUNT = 5000
    sim = boid_engine.Simulation(BOID_COUNT, 1200.0, 800.0)
    
    # Test 1: Time to call get_full_state
    times = []
    for _ in range(1000):
        start = time.perf_counter()
        state = sim.get_full_state()
        end = time.perf_counter()
        times.append((end - start) * 1000000)  # microseconds
    
    avg_time = sum(times) / len(times)
    print(f"get_full_state() average time: {avg_time:.2f} µs")
    
    # Test 2: Check if it's a copy or view
    state1 = sim.get_full_state()
    state2 = sim.get_full_state()
    
    # Check if they share memory
    shares_memory = np.shares_memory(state1, state2)
    print(f"Shares memory between calls: {shares_memory}")
    
    # Test 3: Check if modifying state affects simulation
    original_pos = state1[0, 0]
    state1[0, 0] = 999999.0
    state3 = sim.get_full_state()
    
    if state3[0, 0] == 999999.0:
        print("State is a VIEW (zero-copy) ✓")
    else:
        print("State is a COPY (allocates memory)")
        print("  This means every frame allocates ~156 KB for 5000 boids")
        print("  At 60 FPS, that's ~9 MB/s of allocations!")
    
    # Test 4: Memory layout
    print(f"\nArray properties:")
    print(f"  Shape: {state1.shape}")
    print(f"  Dtype: {state1.dtype}")
    print(f"  Strides: {state1.strides}")
    print(f"  Flags: C_CONTIGUOUS={state1.flags['C_CONTIGUOUS']}, "
          f"F_CONTIGUOUS={state1.flags['F_CONTIGUOUS']}")
    print(f"  Memory size: {state1.nbytes / 1024:.1f} KB")


def test_numpy_operations_efficiency():
    """Test if numpy operations on state are efficient"""
    import boid_engine
    import numpy as np
    
    print(f"\n{'='*60}")
    print(f"NumPy Operations Efficiency Test")
    print(f"{'='*60}\n")
    
    BOID_COUNT = 5000
    sim = boid_engine.Simulation(BOID_COUNT, 1200.0, 800.0)
    
    # Simulate one frame
    predator_pos = boid_engine.Vector2D(600.0, 400.0)
    sim.step(predator_pos)
    
    # Get state
    state = sim.get_full_state()
    pos = state[:, :2]
    vel = state[:, 2:]
    
    # Time each operation
    operations = {
        'norm': lambda: np.linalg.norm(vel, axis=1, keepdims=True),
        'maximum': lambda: np.maximum(np.linalg.norm(vel, axis=1, keepdims=True), 1.0),
        'divide': lambda: vel / np.maximum(np.linalg.norm(vel, axis=1, keepdims=True), 1.0),
        'add': lambda: pos + vel / np.maximum(np.linalg.norm(vel, axis=1, keepdims=True), 1.0) * 2,
        'astype': lambda: pos.astype(np.int32),
    }
    
    print(f"{'Operation':<15} {'Time (µs)':<12} {'Per call'}")
    print(f"{'-'*40}")
    
    for op_name, op_func in operations.items():
        times = []
        for _ in range(1000):
            start = time.perf_counter()
            result = op_func()
            end = time.perf_counter()
            times.append((end - start) * 1000000)
        
        avg = sum(times) / len(times)
        per_boid = avg / BOID_COUNT
        print(f"{op_name:<15} {avg:>8.2f}    {per_boid:>8.4f} ns/boid")
    
    # Complete rendering pipeline
    print(f"\n{'Full pipeline timing:'}")
    times = []
    for _ in range(1000):
        state = sim.get_full_state()
        pos = state[:, :2]
        vel = state[:, 2:]
        
        start = time.perf_counter()
        v_mag = np.linalg.norm(vel, axis=1, keepdims=True)
        v_mag = np.maximum(v_mag, 1.0)
        dir_vec = vel / v_mag
        head_pos = (pos + dir_vec * 2).astype(np.int32)
        tail_pos = (pos - dir_vec * 3).astype(np.int32)
        body_pos = pos.astype(np.int32)
        end = time.perf_counter()
        
        times.append((end - start) * 1000000)
    
    avg = sum(times) / len(times)
    print(f"Complete numpy pipeline: {avg:.2f} µs")


if __name__ == "__main__":
    try:
        import boid_engine
        import numpy as np
        import tracemalloc
    except ImportError as e:
        print(f"ERROR: Missing required module: {e}")
        sys.exit(1)
    
    test_memory_allocations()
    test_get_full_state_overhead()
    test_numpy_operations_efficiency()