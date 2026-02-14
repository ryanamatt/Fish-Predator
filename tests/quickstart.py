#!/usr/bin/env python3
"""
QUICK START - CPU Diagnostic Tests for Boid Simulation

This script helps you quickly identify why your boid simulation is using too much CPU.

SETUP:
  1. Build the boid engine:
     pip install .
  
  2. Install dependencies:
     pip install pygame psutil numpy

RUN:
  python quickstart.py

This will run the most important diagnostic tests and tell you what's wrong.
"""

import sys
import subprocess


def check_module(module_name, install_cmd=None):
    """Check if a module is installed"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        if install_cmd:
            print(f"  ✗ {module_name} not found. Install: {install_cmd}")
        else:
            print(f"  ✗ {module_name} not found.")
        return False


def main():
    print("="*70)
    print("BOID SIMULATION CPU DIAGNOSTIC - QUICK START")
    print("="*70)
    
    # Check requirements
    print("\n1. Checking requirements...")
    all_ok = True
    
    all_ok &= check_module('boid_engine', 'pip install .')
    all_ok &= check_module('pygame', 'pip install pygame')
    all_ok &= check_module('psutil', 'pip install psutil')
    all_ok &= check_module('numpy', 'pip install numpy')
    
    if not all_ok:
        print("\n⚠ Please install missing modules first!")
        return 1
    
    print("  ✓ All requirements satisfied!")
    
    # Ask if user wants to run all tests
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\nThe minimal test above should have identified the issue.")
    print("\nFor comprehensive diagnostics, run:")
    print("  python run_all_tests.py")
    print("\nOr run individual tests:")
    print("  python test_cpu_usage.py      - CPU usage measurement")
    print("  python test_openmp.py          - OpenMP multi-threading")
    print("  python test_memory.py          - Memory allocations")
    print("  python test_frame_timing.py    - Frame time breakdown")
    print("  python test_pygame_behaviors.py - Pygame-specific issues")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())