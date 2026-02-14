"""
Test pygame-specific behaviors that might cause CPU issues.
"""
import time
import psutil
import os


def test_display_flip_vsync():
    """Test if display.flip() is causing issues with VSync"""
    import pygame
    
    print(f"\n{'='*60}")
    print(f"Display Flip & VSync Test")
    print(f"{'='*60}\n")
    
    process = psutil.Process(os.getpid())
    
    # Test with VSync enabled (default)
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    print("Testing display.flip() with default settings...")
    
    flip_times = []
    cpu_samples = []
    
    for i in range(100):
        screen.fill((0, 0, 0))
        
        start = time.perf_counter()
        pygame.display.flip()
        end = time.perf_counter()
        
        flip_times.append((end - start) * 1000)
        
        if i % 10 == 0:
            cpu_samples.append(process.cpu_percent())
        
        time.sleep(0.001)
    
    avg_flip = sum(flip_times) / len(flip_times)
    avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
    
    print(f"  Average flip time: {avg_flip:.2f} ms")
    print(f"  Average CPU: {avg_cpu:.1f}%")
    
    if avg_flip > 16:
        print(f"  ⚠ Flip is taking too long (VSync waiting?)")
    
    pygame.quit()
    
    # Test with NOFRAME and different flags
    print(f"\nTesting with NOFRAME flag...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
    
    flip_times = []
    
    for i in range(100):
        screen.fill((0, 0, 0))
        start = time.perf_counter()
        pygame.display.flip()
        end = time.perf_counter()
        flip_times.append((end - start) * 1000)
        time.sleep(0.001)
    
    avg_flip_noframe = sum(flip_times) / len(flip_times)
    print(f"  Average flip time: {avg_flip_noframe:.2f} ms")
    
    pygame.quit()


def test_event_handling_overhead():
    """Test if event handling is causing issues"""
    import pygame
    
    print(f"\n{'='*60}")
    print(f"Event Handling Overhead Test")
    print(f"{'='*60}\n")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Test with event handling
    print("Testing with event.get()...")
    
    times_with_events = []
    
    for _ in range(1000):
        start = time.perf_counter()
        for event in pygame.event.get():
            pass
        end = time.perf_counter()
        times_with_events.append((end - start) * 1000000)  # microseconds
    
    avg_with = sum(times_with_events) / len(times_with_events)
    print(f"  Average time: {avg_with:.2f} µs")
    
    # Test without event handling
    print("\nTesting without event.get()...")
    
    times_without = []
    
    for _ in range(1000):
        start = time.perf_counter()
        # Do nothing
        end = time.perf_counter()
        times_without.append((end - start) * 1000000)
    
    avg_without = sum(times_without) / len(times_without)
    
    overhead = avg_with - avg_without
    print(f"  Event handling overhead: {overhead:.2f} µs per frame")
    print(f"  At 60 FPS: {overhead * 60:.2f} µs/second")
    
    if overhead > 100:
        print(f"  ⚠ Event handling is taking significant time")
    else:
        print(f"  ✓ Event handling overhead is negligible")
    
    pygame.quit()


def test_surfarray_overhead():
    """Test if surfarray pixel access is causing issues"""
    import pygame
    import numpy as np
    
    print(f"\n{'='*60}")
    print(f"Surfarray Pixel Access Test")
    print(f"{'='*60}\n")
    
    WIDTH, HEIGHT = 1200, 800
    POINT_COUNT = 5000
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    # Generate random points
    points = np.random.randint(0, [WIDTH, HEIGHT], size=(POINT_COUNT, 2))
    color = np.array([255, 255, 255], dtype=np.uint8)
    
    # Method 1: Using surfarray (current method)
    print("Method 1: surfarray.pixels3d() - CURRENT")
    
    times = []
    for _ in range(100):
        screen.fill((0, 0, 0))
        
        start = time.perf_counter()
        pixels = pygame.surfarray.pixels3d(screen)
        
        # Draw points
        mask = ((points[:, 0] >= 0) & (points[:, 0] < WIDTH) & 
                (points[:, 1] >= 0) & (points[:, 1] < HEIGHT))
        valid = points[mask]
        if len(valid) > 0:
            pixels[valid[:, 0], valid[:, 1]] = color
        
        del pixels
        end = time.perf_counter()
        
        times.append((end - start) * 1000)
    
    avg_surfarray = sum(times) / len(times)
    print(f"  Average time: {avg_surfarray:.2f} ms")
    
    # Method 2: Using pygame.draw (alternative)
    print("\nMethod 2: pygame.draw.circle() - ALTERNATIVE")
    
    times = []
    for _ in range(100):
        screen.fill((0, 0, 0))
        
        start = time.perf_counter()
        for point in points[:100]:  # Only first 100 for reasonable test time
            pygame.draw.circle(screen, (255, 255, 255), point, 1)
        end = time.perf_counter()
        
        times.append((end - start) * 1000)
    
    avg_draw = sum(times) / len(times)
    # Scale to all points
    avg_draw_scaled = avg_draw * (POINT_COUNT / 100)
    
    print(f"  Average time (scaled to {POINT_COUNT} points): {avg_draw_scaled:.2f} ms")
    
    # Comparison
    print(f"\n{'='*60}")
    print(f"Comparison:")
    print(f"  surfarray: {avg_surfarray:.2f} ms")
    print(f"  pygame.draw: {avg_draw_scaled:.2f} ms (estimated)")
    
    if avg_surfarray < avg_draw_scaled:
        print(f"  ✓ surfarray is faster (current method is good)")
    else:
        print(f"  ⚠ pygame.draw might be faster")
    
    pygame.quit()


def test_mouse_position_overhead():
    """Test if mouse.get_pos() in tight loop causes issues"""
    import pygame
    
    print(f"\n{'='*60}")
    print(f"Mouse Position Overhead Test")
    print(f"{'='*60}\n")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    print("Testing mouse.get_pos() overhead...")
    
    times = []
    for _ in range(10000):
        start = time.perf_counter()
        mx, my = pygame.mouse.get_pos()
        end = time.perf_counter()
        times.append((end - start) * 1000000)  # microseconds
    
    avg = sum(times) / len(times)
    
    print(f"  Average time: {avg:.2f} µs")
    print(f"  At 60 FPS: {avg * 60:.2f} µs/second")
    
    if avg > 10:
        print(f"  ⚠ Mouse polling is taking significant time")
    else:
        print(f"  ✓ Mouse polling overhead is negligible")
    
    pygame.quit()


def test_different_surface_sizes():
    """Test how window size affects CPU usage"""
    import pygame
    
    print(f"\n{'='*60}")
    print(f"Window Size Impact Test")
    print(f"{'='*60}\n")
    
    sizes = [(800, 600), (1200, 800), (1920, 1080)]
    
    process = psutil.Process(os.getpid())
    
    for width, height in sizes:
        pygame.init()
        screen = pygame.display.set_mode((width, height))
        
        print(f"\nTesting {width}x{height}...")
        
        times = []
        cpu_samples = []
        
        for i in range(60):
            start = time.perf_counter()
            
            screen.fill((15, 15, 20))
            pygame.display.flip()
            
            end = time.perf_counter()
            times.append((end - start) * 1000)
            
            if i % 10 == 0:
                cpu_samples.append(process.cpu_percent())
        
        avg_time = sum(times) / len(times)
        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        
        print(f"  Average frame time: {avg_time:.2f} ms")
        print(f"  Average CPU: {avg_cpu:.1f}%")
        print(f"  Pixels: {width * height:,}")
        
        pygame.quit()
        time.sleep(0.5)


if __name__ == "__main__":
    import sys
    
    try:
        import pygame
        import psutil
        import numpy as np
    except ImportError as e:
        print(f"ERROR: {e}")
        print("Install with: pip install pygame psutil numpy")
        sys.exit(1)
    
    test_display_flip_vsync()
    test_event_handling_overhead()
    test_surfarray_overhead()
    test_mouse_position_overhead()
    test_different_surface_sizes()