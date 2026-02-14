"""
Master test runner for diagnosing CPU usage issues.
Runs all diagnostic tests in sequence.
"""
import sys
import os


def check_requirements():
    """Check if all required packages are installed"""
    required = {
        'boid_engine': 'Build with: pip install .',
        'pygame': 'Install with: pip install pygame',
        'psutil': 'Install with: pip install psutil',
        'numpy': 'Install with: pip install numpy',
    }
    
    missing = []
    for module, install_msg in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(f"  - {module}: {install_msg}")
    
    if missing:
        print("ERROR: Missing required modules:\n")
        print('\n'.join(missing))
        return False
    
    return True


def run_test(test_name, test_module):
    """Run a test module and capture results"""
    print(f"\n{'#'*70}")
    print(f"# RUNNING: {test_name}")
    print(f"{'#'*70}\n")
    
    try:
        __import__(test_module)
        print(f"\n✓ {test_name} completed successfully")
        return True
    except Exception as e:
        print(f"\n✗ {test_name} failed with error:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all diagnostic tests"""
    print("="*70)
    print("Boid Simulation - CPU Usage Diagnostic Suite")
    print("="*70)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    tests = [
        ("CPU Usage Test", "test_cpu_usage"),
        ("OpenMP Test", "test_openmp"),
        ("Memory Test", "test_memory"),
        ("Frame Timing Test", "test_frame_timing"),
    ]
    
    results = {}
    
    for test_name, test_module in tests:
        results[test_name] = run_test(test_name, test_module)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:<10} {test_name}")
    
    print("\n" + "="*70)
    print("DIAGNOSIS RECOMMENDATIONS")
    print("="*70)
    
    print("""
Based on the test results above, common CPU usage issues include:

1. PYGAME clock.tick() BUSY-WAITING:
   - If 'Frame Timing Test' shows high CPU with clock.tick()
   - Solution: Use time.sleep() instead (as shown in gui.py)

2. OPENMP NOT WORKING:
   - If 'OpenMP Test' shows poor multi-threading speedup
   - Solution: Rebuild with proper OpenMP flags
   - Check: echo $OMP_NUM_THREADS

3. EXCESSIVE MEMORY ALLOCATIONS:
   - If 'Memory Test' shows high allocation rates
   - Solution: Use numpy views instead of copies
   - Check: get_full_state() implementation

4. RENDERING BOTTLENECK:
   - If 'Frame Timing Test' shows render time > simulation time
   - Solution: Reduce boid count or optimize rendering

5. NO FRAME LIMITING:
   - If running unlimited FPS (300+)
   - Solution: Always use frame limiting (sleep or clock.tick)

Review the detailed output above to identify your specific issue.
    """)


if __name__ == "__main__":
    main()