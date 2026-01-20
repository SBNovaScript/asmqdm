# asmqdm

x86_64 Assembly implementation of Python's tqdm progress bar library.

```
Processing: 50%|###############---------------| 50/100 [00:05<00:05, 10it/s]
```

## Overview

asmqdm provides a high-performance progress bar for Python loops, with the core rendering logic implemented in x86_64 Assembly. It uses direct Linux syscalls for maximum performance while maintaining a tqdm-compatible Python API.

## Features

- **Pure Assembly Core**: Progress bar rendering, time tracking, and string formatting in x86_64 Assembly
- **tqdm-Compatible API**: Drop-in replacement for basic tqdm usage
- **Direct Syscalls**: No libc dependency in the Assembly code - uses Linux syscalls directly
- **Rate Limiting**: Intelligent update throttling (50ms) to minimize syscall overhead

## Requirements

- Linux x86_64 (AMD or Intel processor)
- NASM (Netwide Assembler)
- Python 3.8+

## Installation

```bash
# Clone the repository
git clone https://github.com/yourname/asmqdm.git
cd asmqdm

# Build the shared library
make

# Install in development mode
make install
```

## Usage

### Basic Iteration

```python
from asmqdm import asmqdm

for i in asmqdm(range(100)):
    # do work
    pass
```

### With Description

```python
for item in asmqdm(items, desc="Processing"):
    process(item)
```

### Using trange

```python
from asmqdm import trange

for i in trange(100):
    # do work
    pass
```

### Manual Update

```python
with asmqdm(total=100, desc="Downloading") as pbar:
    for chunk in download_chunks():
        process(chunk)
        pbar.update(len(chunk))
```

### Disabled Mode

```python
# Useful for non-interactive environments
for i in asmqdm(range(100), disable=True):
    pass
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Python Application              │
│     for i in asmqdm(range(n)):          │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│     Python Wrapper (ctypes FFI)         │
│  - Iterator protocol                    │
│  - Memory management                    │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│    Shared Library (libasmqdm.so)        │
│         x86_64 Assembly                 │
│  - progress_bar_create/update/close     │
│  - Terminal width detection (ioctl)     │
│  - Time tracking (clock_gettime)        │
│  - Integer-to-string conversion         │
│  - Progress bar rendering               │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│      Linux Kernel (syscalls)            │
│  write, ioctl, clock_gettime, mmap      │
└─────────────────────────────────────────┘
```

## Building

```bash
# Build the shared library
make

# Build with debug symbols
make debug

# View disassembly
make disasm

# View exported symbols
make symbols

# Clean build artifacts
make clean
```

## Testing

```bash
# Run tests
python3 tests/run_tests.py

# Run examples
python3 examples/basic_usage.py
```

## API Reference

### asmqdm(iterable=None, desc=None, total=None, leave=True, disable=False, ascii=False)

Create a progress bar.

**Parameters:**
- `iterable`: Iterable to wrap (optional)
- `desc`: Prefix description string
- `total`: Total iterations (inferred from iterable if possible)
- `leave`: Keep progress bar after completion (default: True)
- `disable`: Disable output entirely (default: False)
- `ascii`: Use ASCII characters only (default: False)

**Methods:**
- `update(n=1)`: Increment the counter by n
- `close()`: Close the progress bar
- `refresh()`: Force redraw
- `set_description(desc)`: Update the description

### trange(*args, **kwargs)

Shortcut for `asmqdm(range(*args), **kwargs)`.

## License

MIT
