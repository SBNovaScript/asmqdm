# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in asmqdm, please report it responsibly.

### How to Report

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Email the maintainer directly or use GitHub's private vulnerability reporting feature
3. Include as much detail as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- Acknowledgment of your report within 48 hours
- Regular updates on the status of the fix
- Credit in the release notes (unless you prefer to remain anonymous)

### Scope

Security issues of particular concern for this project include:

- **Memory safety issues** in the Assembly code (buffer overflows, use-after-free)
- **Syscall vulnerabilities** that could lead to privilege escalation
- **Thread safety issues** in async mode that could cause data corruption
- **Path traversal** or arbitrary file access through the shared library loading

### Out of Scope

The following are generally not considered security vulnerabilities:

- Denial of service through resource exhaustion (e.g., very large iteration counts)
- Issues that require local access with the same privileges as the running process
- Issues in development dependencies not shipped with the package

## Security Considerations

### Platform Requirements

asmqdm uses direct Linux syscalls and is designed to run only on Linux x86_64 systems. Running on other platforms is unsupported and may have undefined behavior.

### Shared Library Loading

The Python wrapper loads `libasmqdm.so` using ctypes. The library is loaded from:
1. The package installation directory
2. System library paths

Ensure the shared library comes from a trusted source.

### Memory Management

The Assembly code allocates memory via `mmap` and manages it directly. The Python wrapper ensures proper cleanup through:
- Context manager (`__exit__`)
- Explicit `close()` calls
- Reference counting in normal usage

## Best Practices for Users

- Install asmqdm from trusted sources (official PyPI package or verified repository)
- Keep the package updated to receive security fixes
- Report any suspicious behavior
