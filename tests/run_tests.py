#!/usr/bin/env python3
"""
Simple test runner for asmqdm that doesn't require pytest.
"""

import sys
import time
import traceback

# Add src/python to path for testing
sys.path.insert(0, str(__file__).rsplit("/", 2)[0] + "/src/python")

from asmqdm import asmqdm, trange
from asmqdm import _ffi


def test_iterate_range():
    """Should iterate over range correctly."""
    result = []
    for i in asmqdm(range(10), disable=True):
        result.append(i)
    assert result == list(range(10)), f"Expected {list(range(10))}, got {result}"
    print("  PASS: test_iterate_range")


def test_iterate_list():
    """Should iterate over list correctly."""
    items = ["a", "b", "c"]
    result = []
    for item in asmqdm(items, disable=True):
        result.append(item)
    assert result == items, f"Expected {items}, got {result}"
    print("  PASS: test_iterate_list")


def test_trange():
    """trange should work like asmqdm(range(...))."""
    result = list(trange(5, disable=True))
    assert result == [0, 1, 2, 3, 4], f"Expected [0,1,2,3,4], got {result}"
    print("  PASS: test_trange")


def test_empty_iterable():
    """Should handle empty iterables."""
    result = list(asmqdm([], disable=True))
    assert result == [], f"Expected [], got {result}"
    print("  PASS: test_empty_iterable")


def test_total_inferred():
    """Total should be inferred from iterable."""
    pbar = asmqdm(range(100), disable=True)
    assert pbar.total == 100, f"Expected total=100, got {pbar.total}"
    pbar.close()
    print("  PASS: test_total_inferred")


def test_manual_update():
    """Should support manual update calls."""
    pbar = asmqdm(total=100, disable=True)
    for _ in range(10):
        pbar.update(10)
    assert pbar.n == 100, f"Expected n=100, got {pbar.n}"
    pbar.close()
    print("  PASS: test_manual_update")


def test_context_manager():
    """Should work as context manager."""
    with asmqdm(total=50, disable=True) as pbar:
        for _ in range(5):
            pbar.update(10)
        assert pbar.n == 50, f"Expected n=50, got {pbar.n}"
    print("  PASS: test_context_manager")


def test_description():
    """Should handle description parameter."""
    pbar = asmqdm(total=10, desc="Test", disable=True)
    assert pbar.desc == "Test", f"Expected desc='Test', got {pbar.desc}"
    pbar.close()
    print("  PASS: test_description")


def test_set_description():
    """Should allow changing description."""
    with asmqdm(total=10, desc="Initial", disable=True) as pbar:
        assert pbar.desc == "Initial"
        pbar.set_description("Updated")
        assert pbar.desc == "Updated", f"Expected desc='Updated', got {pbar.desc}"
    print("  PASS: test_set_description")


def test_terminal_width():
    """Should return positive terminal width."""
    width = _ffi.terminal_width()
    assert width > 0, f"Expected positive width, got {width}"
    assert width < 10000, f"Width too large: {width}"
    print(f"  PASS: test_terminal_width (width={width})")


def test_time_ns():
    """Should return monotonic time in nanoseconds."""
    t1 = _ffi.time_ns()
    time.sleep(0.01)
    t2 = _ffi.time_ns()
    assert t2 > t1, f"Expected t2 > t1, got t1={t1}, t2={t2}"
    assert t2 - t1 > 1_000_000, f"Expected >1ms elapsed, got {t2-t1}ns"
    print(f"  PASS: test_time_ns (elapsed={t2-t1}ns)")


def test_len():
    """__len__ should return total."""
    pbar = asmqdm(total=42, disable=True)
    assert len(pbar) == 42, f"Expected len=42, got {len(pbar)}"
    pbar.close()
    print("  PASS: test_len")


def test_format_dict():
    """format_dict should contain n, total, desc."""
    with asmqdm(total=100, desc="Test", disable=True) as pbar:
        pbar.update(50)
        fd = pbar.format_dict
        assert fd["n"] == 50, f"Expected n=50, got {fd['n']}"
        assert fd["total"] == 100, f"Expected total=100, got {fd['total']}"
        assert fd["desc"] == "Test", f"Expected desc='Test', got {fd['desc']}"
    print("  PASS: test_format_dict")


def test_render_without_crash():
    """Should render without crashing."""
    for i in asmqdm(range(10)):
        time.sleep(0.01)
    print()
    print("  PASS: test_render_without_crash")


def test_render_with_description():
    """Should render with description."""
    for i in asmqdm(range(10), desc="Testing"):
        time.sleep(0.01)
    print()
    print("  PASS: test_render_with_description")


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        test_iterate_range,
        test_iterate_list,
        test_trange,
        test_empty_iterable,
        test_total_inferred,
        test_manual_update,
        test_context_manager,
        test_description,
        test_set_description,
        test_terminal_width,
        test_time_ns,
        test_len,
        test_format_dict,
        test_render_without_crash,
        test_render_with_description,
    ]

    passed = 0
    failed = 0
    errors = []

    print("=" * 60)
    print("Running asmqdm tests")
    print("=" * 60)

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append((test_func.__name__, str(e)))
            print(f"  FAIL: {test_func.__name__}: {e}")
        except Exception as e:
            failed += 1
            errors.append((test_func.__name__, traceback.format_exc()))
            print(f"  ERROR: {test_func.__name__}: {e}")

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if errors:
        print("\nFailures:")
        for name, error in errors:
            print(f"  {name}: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
