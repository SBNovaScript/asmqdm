#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026-present Steven Baumann (@SBNovaScript)
# Original repository: https://github.com/SBNovaScript/asmqdm
# See LICENSE and NOTICE in the repository root for details.
# Please retain this header, thank you!

"""
Basic usage examples for asmqdm - Assembly-powered progress bar

This demonstrates the main features of asmqdm, which provides a high-performance
API backed by x86_64 Assembly for high-performance progress bar rendering.
"""

import sys
import time

# Add src/python to path (for development)
sys.path.insert(0, str(__file__).rsplit("/", 2)[0] + "/src/python")

from asmqdm import asmqdm, trange


def example_basic_iteration():
    """Basic iteration over a range."""
    print("\n=== Basic Iteration ===")
    for i in asmqdm(range(100)):
        time.sleep(0.01)  # Simulate work
    print()


def example_with_description():
    """Progress bar with description."""
    print("\n=== With Description ===")
    for i in asmqdm(range(50), desc="Processing"):
        time.sleep(0.02)
    print()


def example_trange():
    """Using trange shortcut."""
    print("\n=== Using trange ===")
    for i in trange(75):
        time.sleep(0.015)
    print()


def example_manual_update():
    """Manual update mode with context manager."""
    print("\n=== Manual Update ===")
    with asmqdm(total=100, desc="Downloading") as pbar:
        for i in range(10):
            time.sleep(0.1)  # Simulate chunk download
            pbar.update(10)
    print()


def example_iterate_list():
    """Iterating over a list."""
    print("\n=== Iterate List ===")
    items = ["apple", "banana", "cherry", "date", "elderberry"]
    for item in asmqdm(items, desc="Fruits"):
        time.sleep(0.3)  # Simulate processing each item
    print()


def example_nested_loops():
    """Nested progress bars (outer only)."""
    print("\n=== Nested Loops ===")
    for i in asmqdm(range(3), desc="Outer"):
        for j in range(20):
            time.sleep(0.02)
    print()


def example_disabled():
    """Disabled progress bar (no output)."""
    print("\n=== Disabled Mode ===")
    print("Running with disable=True (no progress bar shown)...")
    for i in asmqdm(range(100), disable=True):
        time.sleep(0.001)
    print("Done!")


def example_changing_description():
    """Changing description mid-iteration."""
    print("\n=== Dynamic Description ===")
    with asmqdm(total=50, desc="Starting") as pbar:
        for i in range(50):
            if i == 20:
                pbar.set_description("Middle")
            elif i == 40:
                pbar.set_description("Almost done")
            pbar.update(1)
            time.sleep(0.03)
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("asmqdm - Assembly x86_64 Progress Bar Examples")
    print("=" * 60)

    example_basic_iteration()
    example_with_description()
    example_trange()
    example_manual_update()
    example_iterate_list()
    example_nested_loops()
    example_disabled()
    example_changing_description()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
