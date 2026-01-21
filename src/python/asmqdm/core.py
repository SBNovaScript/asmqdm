# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026-present Steven Baumann (@SBNovaScript)
# Original repository: https://github.com/SBNovaScript/asmqdm
# See LICENSE and NOTICE in the repository root for details.
# Please retain this header, thank you!

"""
asmqdm - x86_64 Assembly implementation of tqdm progress bar

This module provides a tqdm-compatible API backed by an Assembly
implementation for maximum performance on Linux x86_64 systems.

Usage:
    from asmqdm import asmqdm

    # Wrap an iterable
    for i in asmqdm(range(100)):
        do_work()

    # With description
    for item in asmqdm(items, desc="Processing"):
        process(item)

    # Manual update
    with asmqdm(total=100) as pbar:
        for i in range(10):
            pbar.update(10)
"""

import sys
from typing import Any, Iterable, Iterator, Optional, TypeVar

from . import _ffi

T = TypeVar('T')


class asmqdm:
    """
    Assembly-powered progress bar iterator.

    A drop-in replacement for tqdm that uses x86_64 Assembly for
    the core progress bar rendering logic.

    Parameters
    ----------
    iterable : Iterable[T], optional
        Iterable to wrap. If not provided, must specify `total`.
    desc : str, optional
        Prefix description for the progress bar.
    total : int, optional
        Total number of iterations. Inferred from iterable if possible.
    leave : bool, default True
        Whether to leave the progress bar visible after completion.
    disable : bool, default False
        Whether to disable the progress bar entirely.
        Useful for non-TTY output or when running in quiet mode.
    ascii : bool, default False
        Use ASCII characters only for the progress bar.
    file : file-like, optional
        Output file (unused, for tqdm compatibility).
    ncols : int, optional
        Width of the progress bar (auto-detected if not specified).
    unit : str, default "it"
        Unit name (unused, for tqdm compatibility).
    async_render : bool, default False
        Enable async rendering mode with dedicated render thread.
        - Rendering happens on a separate CPU core
        - update() becomes a lock-free atomic increment (~5-10ns vs ~500ns)
        - Best for high-frequency updates (>10,000/sec)

    Examples
    --------
    >>> from asmqdm import asmqdm
    >>> for i in asmqdm(range(100)):
    ...     pass

    >>> # High-performance async mode
    >>> for i in asmqdm(range(1000000), async_render=True):
    ...     pass

    >>> with asmqdm(total=50, desc="Working") as pbar:
    ...     for i in range(5):
    ...         pbar.update(10)
    """

    def __init__(
        self,
        iterable: Optional[Iterable[T]] = None,
        desc: Optional[str] = None,
        total: Optional[int] = None,
        leave: bool = True,
        disable: bool = False,
        ascii: bool = False,
        file: Any = None,
        ncols: Optional[int] = None,
        unit: str = "it",
        async_render: bool = False,
    ) -> None:
        self.iterable = iterable
        self.desc = desc
        self.leave = leave
        self.disable = disable
        self.ascii_only = ascii
        self.async_render = async_render

        # Determine total iterations
        if total is not None:
            self.total = total
        elif iterable is not None and hasattr(iterable, '__len__'):
            self.total = len(iterable)  # type: ignore
        else:
            self.total = 0  # Unknown length

        # Create assembly progress bar state
        self._state = None
        self._closed = False
        self._is_async = False
        # Keep reference to desc_bytes to prevent garbage collection
        self._desc_bytes: Optional[bytes] = None

        if not self.disable:
            self._desc_bytes = self.desc.encode('utf-8') if self.desc else None

            if async_render:
                # Async mode: dedicated render thread, lock-free updates
                self._state = _ffi.create_async(
                    self.total,
                    desc_bytes=self._desc_bytes,
                    leave=self.leave,
                    disable=self.disable,
                    ascii_only=self.ascii_only,
                )
                self._is_async = True
            else:
                # Sync mode: traditional rendering
                self._state = _ffi.create(
                    self.total,
                    desc_bytes=self._desc_bytes,
                    leave=self.leave,
                    disable=self.disable,
                    ascii_only=self.ascii_only,
                )

        self._iterator: Optional[Iterator[T]] = None
        self.n = 0  # Current iteration count

    def __iter__(self) -> 'asmqdm':
        """Return iterator over wrapped iterable."""
        if self.iterable is not None:
            self._iterator = iter(self.iterable)
        return self

    def __next__(self) -> T:
        """Get next item and update progress bar."""
        if self._iterator is None:
            raise StopIteration

        try:
            item = next(self._iterator)
            self.update(1)
            return item
        except StopIteration:
            self.close()
            raise

    def __enter__(self) -> 'asmqdm':
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Context manager exit."""
        self.close()
        return False

    def __len__(self) -> int:
        """Return total iterations."""
        return self.total

    def update(self, n: int = 1) -> None:
        """
        Manually update the progress bar.

        In async mode, this is a lock-free atomic increment (~5-10ns).
        In sync mode, this may trigger a render (~500-1000ns).

        Parameters
        ----------
        n : int, default 1
            Number of iterations to increment by.
        """
        if self._state is not None and not self._closed:
            if self._is_async:
                self.n = _ffi.update_async(self._state, n)
            else:
                self.n = _ffi.update(self._state, n)
        else:
            # Still track count even when disabled
            self.n += n

    def close(self) -> None:
        """Close the progress bar and release resources."""
        if self._state is not None and not self._closed:
            if self._is_async:
                _ffi.close_async(self._state)
            else:
                _ffi.close(self._state)
            self._state = None
            self._closed = True

    def refresh(self) -> None:
        """Force refresh the display."""
        if self._state is not None and not self._closed:
            _ffi.render(self._state)

    def set_description(self, desc: Optional[str] = None) -> None:
        """
        Update the description prefix.

        Parameters
        ----------
        desc : str, optional
            New description. Pass None to clear.
        """
        self.desc = desc
        if self._state is not None and not self._closed:
            # Keep reference to new desc_bytes
            self._desc_bytes = desc.encode('utf-8') if desc else b""
            _ffi.set_description(self._state, self._desc_bytes)

    def set_postfix(self, **kwargs: Any) -> None:
        """
        Set postfix info (stub for tqdm compatibility).

        Note: This is not yet implemented in the Assembly backend.
        """
        pass  # TODO: Implement if needed

    @staticmethod
    def write(
        s: str,
        file: Any = None,
        end: str = "\n",
        nolock: bool = False,
    ) -> None:
        """
        Print a message without interfering with progress bars.

        Parameters
        ----------
        s : str
            Message to print.
        file : file-like, optional
            Output file (defaults to stderr).
        end : str, default "\\n"
            String to append after the message.
        nolock : bool, default False
            Ignored (for tqdm compatibility).
        """
        output = file if file is not None else sys.stderr
        # Clear line, print message, then progress bar will redraw
        output.write('\r\033[K')  # Carriage return + clear line
        output.write(s)
        output.write(end)
        output.flush()

    @property
    def format_dict(self) -> dict:
        """
        Return a dict with progress bar stats (for tqdm compatibility).
        """
        return {
            'n': self.n,
            'total': self.total,
            'desc': self.desc,
        }


def trange(*args: Any, **kwargs: Any) -> asmqdm:
    """
    Shortcut for asmqdm(range(*args), **kwargs).

    Parameters
    ----------
    *args : int
        Arguments passed to range().
    **kwargs : Any
        Arguments passed to asmqdm().

    Returns
    -------
    asmqdm
        Progress bar wrapping a range object.

    Examples
    --------
    >>> from asmqdm import trange
    >>> for i in trange(100):
    ...     pass
    """
    return asmqdm(range(*args), **kwargs)
