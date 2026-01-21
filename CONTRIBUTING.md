# Contributing to asmqdm

Thank you for your interest in contributing to asmqdm! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

* Linux x86_64 (required — the Assembly code uses Linux system calls)
* NASM (Netwide Assembler)
* Python 3.8+
* uv package manager (recommended) or pip

### Getting Started

1. Fork the repository on GitHub

2. Clone your fork:

   ```bash
   git clone https://github.com/YOUR_USERNAME/asmqdm.git
   cd asmqdm
   ```

3. Install NASM if not already installed:

   ```bash
   # Debian/Ubuntu
   sudo apt-get install nasm

   # Fedora
   sudo dnf install nasm

   # Arch Linux
   sudo pacman -S nasm
   ```

4. Build the shared library:

   ```bash
   make
   ```

5. Install in development mode:

   ```bash
   make install
   ```

6. Run tests to verify setup:

   ```bash
   make test
   ```

## Project Structure

```
asmqdm/
├── src/
│   ├── asm/                    # x86_64 Assembly implementation
│   │   ├── asmqdm.asm           # Main library source
│   │   └── include/
│   │       └── constants.inc    # Syscall numbers, constants
│   └── python/
│       └── asmqdm/              # Python package
│           ├── __init__.py      # Public API
│           ├── core.py          # asmqdm class
│           └── _ffi.py          # ctypes FFI bindings
├── tests/                       # Test suite
├── examples/                    # Usage examples
└── build/                       # Build artifacts (generated)
```

## Making Changes

### Code Style

**Python:**

* Follow PEP 8 guidelines
* Use descriptive variable names
* Add docstrings for public functions and classes
* Keep functions focused and reasonably sized

**Assembly:**

* Use clear section headers and comments
* Document syscall usage and register conventions
* Follow the existing code structure for new functions
* Preserve callee-saved registers (rbx, rbp, r12-r15)

### Testing

* Add tests for new functionality
* Ensure all existing tests pass before submitting
* Run the test suite:

  ```bash
  make test
  # or
  python tests/run_tests.py
  ```

### Benchmarking

If your change affects performance, run the benchmark suite:

```bash
python tests/benchmark.py
```

## Submitting Changes

### Pull Request Process

1. Create a feature branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes with clear, focused commits

3. Write descriptive commit messages:

   ```
   Add async rendering mode with CPU affinity

   - Implement clone() syscall for thread creation
   - Add lock-free atomic counter updates
   - Set CPU affinity for render thread isolation
   ```

4. Push to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a Pull Request against the `main` branch

### PR Guidelines

* Provide a clear description of what the PR does
* Reference any related issues
* Include test results if applicable
* Keep PRs focused — one feature or fix per PR

## Licensing and Developer Certificate of Origin

### License of Contributions

By contributing to asmqdm, you agree that your contributions will be licensed under the Apache License, Version 2.0.

### Third-Party Code

Do not copy code from third-party sources unless the source’s license is compatible with Apache-2.0 and you have the right to contribute it under Apache-2.0. If you’re unsure, call it out in the PR description and link the source and license.

### File Headers for New Source Files

New source files should include the project’s SPDX/copyright header at the top. Use the canonical form below.

**Python (.py) header:**

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026-present Steven Baumann (@SBNovaScript)
# Original repository: https://github.com/SBNovaScript/asmqdm
# See LICENSE and NOTICE in the repository root for details.
# Please retain this header, thank you!
```

**NASM (.asm) header:**

```asm
; SPDX-License-Identifier: Apache-2.0
; Copyright (c) 2026-present Steven Baumann (@SBNovaScript)
; Original repository: https://github.com/SBNovaScript/asmqdm
; See LICENSE and NOTICE in the repository root for details.
; Please retain this header, thank you!
```

### Developer Certificate of Origin (DCO)

This project uses the Developer Certificate of Origin, version 1.1 (DCO). By signing off on a commit, you certify the following:

Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
[https://developercertificate.org/](https://developercertificate.org/)

(a) The contribution was created in whole or in part by me and I have the right to submit it under the open source license indicated in the file; or

(b) The contribution is based upon previous work that, to the best of my knowledge, is covered under an appropriate open source license and I have the right under that license to submit that work with modifications, whether created in whole or in part by me, under the same open source license (unless I am permitted to submit under a different license), as indicated in the file; or

(c) The contribution was provided directly to me by some other person who certified (a), (b) or (c) and I have not modified it.

(d) I understand and agree that this project and the contribution are public and that a record of the contribution (including all personal information I submit with it, including my sign-off) is maintained indefinitely and may be redistributed consistent with this project or the open source license(s) involved.

### Sign-Off Process

All commits must include a DCO sign-off line:

```
Signed-off-by: Your Name <your.email@example.com>
```

You can do this automatically by using the `-s` flag when committing:

```bash
git commit -s -m "Your commit message"
```

If you’ve already made commits without sign-off, you can amend the most recent commit:

```bash
git commit --amend -s
```

Or rebase to sign off multiple commits:

```bash
git rebase --signoff HEAD~N  # where N is the number of commits
```

Please use a name and email that accurately identify you as the contributor.

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

* Python version and OS details
* Steps to reproduce the issue
* Expected vs actual behavior
* Any error messages or tracebacks

### Feature Requests

Feature requests are welcome! Please describe:

* The use case for the feature
* How it would benefit users
* Any implementation ideas you have

### Documentation

Documentation improvements are always appreciated:

* Fix typos or unclear explanations
* Add examples for existing features
* Improve API documentation

### Code Contributions

Areas where contributions are especially welcome:

* Performance optimizations
* Additional tqdm compatibility features
* Better error handling and messages
* Test coverage improvements

## Architecture Notes

### Assembly Layer

The Assembly code (`src/asm/asmqdm.asm`) implements:

* Memory allocation via `mmap` syscall
* Terminal width detection via `ioctl`
* Time tracking via `clock_gettime`
* Progress bar string formatting and rendering
* Async mode with thread creation via `clone`

Key conventions:

* All public functions follow System V AMD64 ABI
* State is stored in mmap’d memory regions
* Render throttling at 50ms intervals

### Python Layer

The Python wrapper (`src/python/asmqdm/`) provides:

* ctypes foreign function interface (FFI) bindings to the shared library
* Iterator protocol implementation
* Context manager support
* tqdm-compatible API

## Questions?

If you have questions about contributing, feel free to:

* Open an issue for discussion
* Check existing issues for similar questions

Thank you for contributing to asmqdm!
