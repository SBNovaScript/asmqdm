# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026-present Steven Baumann (@SBNovaScript)
# Original repository: https://github.com/SBNovaScript/asmqdm
# See LICENSE and NOTICE in the repository root for details.
# Please retain this header, thank you!

"""
Tests for asmqdm - Assembly-based progress bar library
"""

import sys
import time

import pytest

# Add src/python to path for testing
sys.path.insert(0, str(__file__).rsplit("/", 2)[0] + "/src/python")

from asmqdm import asmqdm, trange


class TestBasicIteration:
    """Test basic iteration functionality."""

    def test_iterate_range(self):
        """Should iterate over range correctly."""
        result = []
        for i in asmqdm(range(10), disable=True):
            result.append(i)
        assert result == list(range(10))

    def test_iterate_list(self):
        """Should iterate over list correctly."""
        items = ["a", "b", "c"]
        result = []
        for item in asmqdm(items, disable=True):
            result.append(item)
        assert result == items

    def test_trange(self):
        """trange should work like asmqdm(range(...))."""
        result = list(trange(5, disable=True))
        assert result == [0, 1, 2, 3, 4]

    def test_empty_iterable(self):
        """Should handle empty iterables."""
        result = list(asmqdm([], disable=True))
        assert result == []

    def test_total_inferred_from_list(self):
        """Total should be inferred from list length."""
        pbar = asmqdm([1, 2, 3], disable=True)
        assert pbar.total == 3

    def test_total_inferred_from_range(self):
        """Total should be inferred from range length."""
        pbar = asmqdm(range(100), disable=True)
        assert pbar.total == 100


class TestManualUpdate:
    """Test manual update mode."""

    def test_manual_update(self):
        """Should support manual update calls."""
        pbar = asmqdm(total=100, disable=True)
        for _ in range(10):
            pbar.update(10)
        assert pbar.n == 100
        pbar.close()

    def test_context_manager(self):
        """Should work as context manager."""
        with asmqdm(total=50, disable=True) as pbar:
            for _ in range(5):
                pbar.update(10)
            assert pbar.n == 50

    def test_increment_by_one(self):
        """Default increment should be 1."""
        with asmqdm(total=10, disable=True) as pbar:
            pbar.update()
            pbar.update()
            pbar.update()
            assert pbar.n == 3


class TestDescription:
    """Test description functionality."""

    def test_with_description(self):
        """Should handle description parameter."""
        pbar = asmqdm(total=10, desc="Test", disable=True)
        assert pbar.desc == "Test"
        pbar.close()

    def test_set_description(self):
        """Should allow changing description."""
        with asmqdm(total=10, desc="Initial", disable=True) as pbar:
            assert pbar.desc == "Initial"
            pbar.set_description("Updated")
            assert pbar.desc == "Updated"

    def test_no_description(self):
        """Should work without description."""
        pbar = asmqdm(total=10, disable=True)
        assert pbar.desc is None
        pbar.close()


class TestFlags:
    """Test flag options."""

    def test_disable_flag(self):
        """Disabled progress bar should not render."""
        # Just verify it doesn't crash
        for i in asmqdm(range(5), disable=True):
            pass

    def test_leave_default_true(self):
        """Leave should default to True."""
        pbar = asmqdm(total=10, disable=True)
        assert pbar.leave is True
        pbar.close()

    def test_leave_false(self):
        """Should accept leave=False."""
        pbar = asmqdm(total=10, leave=False, disable=True)
        assert pbar.leave is False
        pbar.close()


class TestOutput:
    """Test progress bar output (visual tests)."""

    def test_renders_without_crash(self, capsys):
        """Should render without crashing."""
        for i in asmqdm(range(5)):
            time.sleep(0.01)
        # Just checking it doesn't crash

    def test_with_description_renders(self, capsys):
        """Should render with description."""
        for i in asmqdm(range(5), desc="Processing"):
            time.sleep(0.01)
        # Just checking it doesn't crash

    def test_trange_renders(self, capsys):
        """trange should render properly."""
        for i in trange(5):
            time.sleep(0.01)


class TestFormatDict:
    """Test format_dict property."""

    def test_format_dict_contains_n(self):
        """format_dict should contain current iteration count."""
        with asmqdm(total=10, disable=True) as pbar:
            pbar.update(5)
            assert pbar.format_dict["n"] == 5

    def test_format_dict_contains_total(self):
        """format_dict should contain total."""
        with asmqdm(total=100, disable=True) as pbar:
            assert pbar.format_dict["total"] == 100

    def test_format_dict_contains_desc(self):
        """format_dict should contain description."""
        with asmqdm(total=10, desc="Test", disable=True) as pbar:
            assert pbar.format_dict["desc"] == "Test"


class TestLen:
    """Test __len__ method."""

    def test_len_returns_total(self):
        """__len__ should return total."""
        pbar = asmqdm(total=42, disable=True)
        assert len(pbar) == 42
        pbar.close()


class TestFFI:
    """Test low-level FFI functions."""

    def test_terminal_width(self):
        """Should return positive terminal width."""
        from asmqdm import _ffi

        width = _ffi.terminal_width()
        assert width > 0
        assert width < 10000  # Sanity check

    def test_time_ns(self):
        """Should return monotonic time in nanoseconds."""
        from asmqdm import _ffi

        t1 = _ffi.time_ns()
        time.sleep(0.01)
        t2 = _ffi.time_ns()
        # Should have elapsed at least 10ms = 10,000,000 ns
        assert t2 > t1
        assert t2 - t1 > 1_000_000  # At least 1ms


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
