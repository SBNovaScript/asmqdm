# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026-present Steven Baumann (@SBNovaScript)
# Original repository: https://github.com/SBNovaScript/asmqdm
# See LICENSE and NOTICE in the repository root for details.
# Please retain this header, thank you!

"""
Low-level ctypes bindings to libasmqdm.so

This module provides direct access to the Assembly-implemented
progress bar functions via Python's ctypes FFI.
"""

import ctypes
from pathlib import Path
from typing import Optional


def _find_library() -> str:
    """Locate libasmqdm.so shared library."""
    # Check multiple possible locations
    locations = [
        # Same directory as this module (installed)
        Path(__file__).parent / "libasmqdm.so",
        # Build directory (development)
        Path(__file__).parent.parent.parent.parent / "build" / "libasmqdm.so",
        # System locations
        Path("/usr/local/lib/libasmqdm.so"),
        Path("/usr/lib/libasmqdm.so"),
    ]

    for loc in locations:
        if loc.exists():
            return str(loc.resolve())

    raise OSError(
        "Could not find libasmqdm.so. "
        "Make sure to run 'make' first to build the library."
    )


# Load the shared library
_lib: Optional[ctypes.CDLL] = None


def _get_lib() -> ctypes.CDLL:
    """Get or load the shared library (lazy loading)."""
    global _lib
    if _lib is None:
        _lib = ctypes.CDLL(_find_library())
        _setup_functions(_lib)
    return _lib


def _setup_functions(lib: ctypes.CDLL) -> None:
    """Configure function signatures for the library."""

    # progress_bar_create(total, desc_ptr, desc_len, flags) -> state*
    lib.progress_bar_create.argtypes = [
        ctypes.c_int64,     # total
        ctypes.c_char_p,    # desc_ptr
        ctypes.c_int64,     # desc_len
        ctypes.c_uint64,    # flags
    ]
    lib.progress_bar_create.restype = ctypes.c_void_p

    # progress_bar_update(state*, increment) -> current
    lib.progress_bar_update.argtypes = [
        ctypes.c_void_p,    # state pointer
        ctypes.c_int64,     # increment
    ]
    lib.progress_bar_update.restype = ctypes.c_int64

    # progress_bar_render(state*) -> void
    lib.progress_bar_render.argtypes = [ctypes.c_void_p]
    lib.progress_bar_render.restype = None

    # progress_bar_close(state*) -> void
    lib.progress_bar_close.argtypes = [ctypes.c_void_p]
    lib.progress_bar_close.restype = None

    # progress_bar_set_description(state*, desc_ptr, desc_len) -> void
    lib.progress_bar_set_description.argtypes = [
        ctypes.c_void_p,    # state pointer
        ctypes.c_char_p,    # desc_ptr
        ctypes.c_int64,     # desc_len
    ]
    lib.progress_bar_set_description.restype = None

    # get_terminal_width() -> width
    lib.get_terminal_width.argtypes = []
    lib.get_terminal_width.restype = ctypes.c_int64

    # get_time_ns() -> nanoseconds
    lib.get_time_ns.argtypes = []
    lib.get_time_ns.restype = ctypes.c_int64

    # Async functions
    # progress_bar_create_async(total, desc_ptr, desc_len, flags) -> state*
    lib.progress_bar_create_async.argtypes = [
        ctypes.c_int64,     # total
        ctypes.c_char_p,    # desc_ptr
        ctypes.c_int64,     # desc_len
        ctypes.c_uint64,    # flags
    ]
    lib.progress_bar_create_async.restype = ctypes.c_void_p

    # progress_bar_update_async(state*, increment) -> current
    lib.progress_bar_update_async.argtypes = [
        ctypes.c_void_p,    # state pointer
        ctypes.c_int64,     # increment
    ]
    lib.progress_bar_update_async.restype = ctypes.c_int64

    # progress_bar_close_async(state*) -> void
    lib.progress_bar_close_async.argtypes = [ctypes.c_void_p]
    lib.progress_bar_close_async.restype = None


# Flag constants (must match constants.inc)
FLAG_LEAVE = 0x01
FLAG_DISABLE = 0x02
FLAG_ASCII = 0x04
FLAG_ASYNC = 0x20


def create(
    total: int,
    desc_bytes: Optional[bytes] = None,
    leave: bool = True,
    disable: bool = False,
    ascii_only: bool = False,
) -> ctypes.c_void_p:
    """
    Create a new progress bar state.

    Args:
        total: Total number of iterations
        desc_bytes: Optional description as bytes (caller must keep reference!)
        leave: Whether to leave progress bar visible after completion
        disable: Whether to disable output entirely
        ascii_only: Whether to use ASCII-only characters

    Returns:
        Pointer to the progress bar state (opaque handle)
    """
    lib = _get_lib()

    flags = 0
    if leave:
        flags |= FLAG_LEAVE
    if disable:
        flags |= FLAG_DISABLE
    if ascii_only:
        flags |= FLAG_ASCII

    desc_len = len(desc_bytes) if desc_bytes else 0

    return lib.progress_bar_create(total, desc_bytes, desc_len, flags)


def update(state: ctypes.c_void_p, n: int = 1) -> int:
    """
    Update progress by n iterations.

    Args:
        state: Progress bar state pointer
        n: Number of iterations to increment by

    Returns:
        Current iteration count
    """
    lib = _get_lib()
    return lib.progress_bar_update(state, n)


def render(state: ctypes.c_void_p) -> None:
    """
    Force render the progress bar.

    Args:
        state: Progress bar state pointer
    """
    lib = _get_lib()
    lib.progress_bar_render(state)


def close(state: ctypes.c_void_p) -> None:
    """
    Close and cleanup the progress bar.

    Args:
        state: Progress bar state pointer
    """
    lib = _get_lib()
    lib.progress_bar_close(state)


def set_description(state: ctypes.c_void_p, desc_bytes: bytes) -> None:
    """
    Update the description prefix.

    Args:
        state: Progress bar state pointer
        desc_bytes: New description as bytes (caller must keep reference!)
    """
    lib = _get_lib()
    lib.progress_bar_set_description(state, desc_bytes, len(desc_bytes))


def terminal_width() -> int:
    """
    Get current terminal width.

    Returns:
        Terminal width in characters
    """
    lib = _get_lib()
    return lib.get_terminal_width()


def time_ns() -> int:
    """
    Get current monotonic time in nanoseconds.

    Returns:
        Nanoseconds since system boot
    """
    lib = _get_lib()
    return lib.get_time_ns()


# ============================================
# ASYNC FUNCTIONS
# ============================================

def create_async(
    total: int,
    desc_bytes: Optional[bytes] = None,
    leave: bool = True,
    disable: bool = False,
    ascii_only: bool = False,
) -> ctypes.c_void_p:
    """
    Create a new async progress bar with dedicated render thread.

    The render thread runs on a separate CPU core (if available) and
    handles all rendering independently. Updates are lock-free atomic
    increments with minimal overhead.

    Args:
        total: Total number of iterations
        desc_bytes: Optional description as bytes (caller must keep reference!)
        leave: Whether to leave progress bar visible after completion
        disable: Whether to disable output entirely
        ascii_only: Whether to use ASCII-only characters

    Returns:
        Pointer to the progress bar state (opaque handle)
    """
    lib = _get_lib()

    flags = FLAG_ASYNC  # Always set async flag
    if leave:
        flags |= FLAG_LEAVE
    if disable:
        flags |= FLAG_DISABLE
    if ascii_only:
        flags |= FLAG_ASCII

    desc_len = len(desc_bytes) if desc_bytes else 0

    return lib.progress_bar_create_async(total, desc_bytes, desc_len, flags)


def update_async(state: ctypes.c_void_p, n: int = 1) -> int:
    """
    Atomic lock-free progress update.

    This is extremely fast - just a single atomic increment instruction.
    The render thread handles all display updates asynchronously.

    Args:
        state: Progress bar state pointer
        n: Number of iterations to increment by

    Returns:
        New current iteration count
    """
    lib = _get_lib()
    return lib.progress_bar_update_async(state, n)


def close_async(state: ctypes.c_void_p) -> None:
    """
    Close async progress bar and stop render thread.

    Signals the render thread to shutdown, waits for it to exit,
    performs a final render, then cleans up all resources.

    Args:
        state: Progress bar state pointer
    """
    lib = _get_lib()
    lib.progress_bar_close_async(state)
