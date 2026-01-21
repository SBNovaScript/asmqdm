# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-01-21

### Added

- Initial release of asmqdm
- Core progress bar implementation in x86_64 Assembly
- Python wrapper with tqdm-compatible API
- `asmqdm` class with iterator protocol support
- `trange` helper function for range iteration
- Context manager support for manual update mode
- Description prefix support with `desc` parameter
- Dynamic description updates with `set_description()`
- Async rendering mode with dedicated render thread
- CPU affinity for render thread isolation
- Lock-free atomic updates in async mode
- Terminal width auto-detection via ioctl
- Intelligent render throttling (50ms minimum interval)
- Direct Linux syscalls (no libc dependency in Assembly)
- Support for Python 3.8 through 3.12
- Comprehensive test suite
- Usage examples and documentation

### Technical Details

- Memory allocation via `mmap` syscall
- Thread creation via `clone` syscall for async mode
- Nanosecond-precision timing via `clock_gettime`
- System V AMD64 ABI compliance for all exported functions

[Unreleased]: https://github.com/SBNovaScript/asmqdm/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/SBNovaScript/asmqdm/releases/tag/v0.1.0
