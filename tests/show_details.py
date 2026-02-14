"""
Run detailed diagnostics with full output
"""
import subprocess
import sys

tests = [
    ("CPU Usage", "test_cpu_usage.py"),
    ("OpenMP Threading", "test_openmp.py"),
    ("Memory Allocations", "test_memory.py"),
    ("Frame Timing", "test_frame_timing.py"),
    ("Minimal Repro (clock.tick)", "test_minimal_repro.py"),
]

print("="*70)
print("DETAILED CPU DIAGNOSTICS - FULL OUTPUT")
print("="*70)

for test_name, test_file in tests:
    print("\n" + "#"*70)
    print(f"# {test_name}")
    print("#"*70 + "\n")
    
    result = subprocess.run([sys.executable, f"tests/{test_file}"])
    
    if result.returncode != 0:
        print(f"\n⚠ {test_name} encountered an error")
    
    print("\n" + "-"*70)

print("\n" + "="*70)
print("ALL DIAGNOSTICS COMPLETE")
print("="*70)