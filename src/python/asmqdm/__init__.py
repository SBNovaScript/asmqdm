# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026-present Steven Baumann (@SBNovaScript)
# Original repository: https://github.com/SBNovaScript/asmqdm
# See LICENSE and NOTICE in the repository root for details.
# Please retain this header, thank you!

"""
asmqdm - x86_64 Assembly implementation of tqdm progress bar

A high-performance progress bar library implemented in x86_64 Assembly
with a Python wrapper for seamless integration.

Basic usage:
    from asmqdm import asmqdm, trange

    # Wrap any iterable
    for item in asmqdm(my_list):
        process(item)

    # Use trange for range iteration
    for i in trange(100):
        do_work()

    # Manual updates with context manager
    with asmqdm(total=100, desc="Processing") as pbar:
        for i in range(10):
            pbar.update(10)
"""

from .core import asmqdm, trange

__version__ = "0.1.0"
__all__ = ["asmqdm", "trange", "__version__"]
