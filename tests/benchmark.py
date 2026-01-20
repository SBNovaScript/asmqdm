#!/usr/bin/env python3
"""
Benchmark script comparing sync vs async asmqdm performance.

Measures the overhead of update() calls in both modes.
"""

import sys
import time

# Add src/python to path
sys.path.insert(0, str(__file__).rsplit("/", 2)[0] + "/src/python")

from asmqdm import asmqdm


def benchmark_sync(n: int, disable_output: bool = False) -> tuple:
    """Benchmark synchronous mode."""
    start = time.perf_counter_ns()
    for i in asmqdm(range(n), disable=disable_output):
        pass
    elapsed = time.perf_counter_ns() - start
    return elapsed, elapsed / n


def benchmark_async(n: int, disable_output: bool = False) -> tuple:
    """Benchmark asynchronous mode."""
    start = time.perf_counter_ns()
    for i in asmqdm(range(n), async_render=True, disable=disable_output):
        pass
    elapsed = time.perf_counter_ns() - start
    return elapsed, elapsed / n


def benchmark_baseline(n: int) -> tuple:
    """Benchmark pure Python loop (baseline)."""
    start = time.perf_counter_ns()
    for i in range(n):
        pass
    elapsed = time.perf_counter_ns() - start
    return elapsed, elapsed / n


def benchmark_manual_update_sync(n: int) -> tuple:
    """Benchmark manual update calls in sync mode."""
    start = time.perf_counter_ns()
    pbar = asmqdm(total=n, disable=True)
    for _ in range(n):
        pbar.update(1)
    pbar.close()
    elapsed = time.perf_counter_ns() - start
    return elapsed, elapsed / n


def benchmark_manual_update_async(n: int) -> tuple:
    """Benchmark manual update calls in async mode."""
    start = time.perf_counter_ns()
    pbar = asmqdm(total=n, async_render=True, disable=True)
    for _ in range(n):
        pbar.update(1)
    pbar.close()
    elapsed = time.perf_counter_ns() - start
    return elapsed, elapsed / n


def format_time(ns: float) -> str:
    """Format nanoseconds in a human-readable way."""
    if ns < 1000:
        return f"{ns:.1f}ns"
    elif ns < 1_000_000:
        return f"{ns/1000:.1f}us"
    elif ns < 1_000_000_000:
        return f"{ns/1_000_000:.1f}ms"
    else:
        return f"{ns/1_000_000_000:.2f}s"


def run_benchmarks():
    """Run all benchmarks and report results."""
    print("=" * 70)
    print("asmqdm Performance Benchmarks")
    print("=" * 70)
    print()

    # Warmup
    print("Warming up...")
    list(range(10000))
    benchmark_sync(1000, disable_output=True)
    try:
        benchmark_async(1000, disable_output=True)
        async_available = True
    except Exception as e:
        print(f"Async mode not available: {e}")
        async_available = False
    print()

    # Test iterations
    test_sizes = [10_000, 100_000, 1_000_000]

    for n in test_sizes:
        print(f"--- {n:,} iterations ---")
        print()

        # Baseline
        total, per_iter = benchmark_baseline(n)
        print(f"Baseline (pure Python):     {format_time(total):>10} total, {format_time(per_iter):>8}/iter")

        # Sync with rendering disabled
        total, per_iter = benchmark_manual_update_sync(n)
        print(f"Sync mode (disabled):       {format_time(total):>10} total, {format_time(per_iter):>8}/iter")

        # Async with rendering disabled
        if async_available:
            total, per_iter = benchmark_manual_update_async(n)
            print(f"Async mode (disabled):      {format_time(total):>10} total, {format_time(per_iter):>8}/iter")

        print()

    # Visual benchmark (with rendering)
    print("--- Visual Benchmarks (with rendering) ---")
    print()

    n = 100_000
    print(f"Sync mode ({n:,} iterations):")
    total, per_iter = benchmark_sync(n)
    print()
    print(f"  Total: {format_time(total)}, Per iteration: {format_time(per_iter)}")
    print()

    if async_available:
        print(f"Async mode ({n:,} iterations):")
        total_async, per_iter_async = benchmark_async(n)
        print()
        print(f"  Total: {format_time(total_async)}, Per iteration: {format_time(per_iter_async)}")
        print()

        if per_iter > 0 and per_iter_async > 0:
            speedup = per_iter / per_iter_async
            print(f"Speedup: {speedup:.1f}x faster update() calls in async mode")

    print()
    print("=" * 70)
    print("Benchmark complete!")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmarks()
