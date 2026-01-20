; asmqdm - Constants and macros for x86_64 Linux
; =============================================

; Use RIP-relative addressing by default (required for shared library)
DEFAULT REL

; ============================================
; Linux x86_64 Syscall Numbers
; ============================================
%define SYS_write           1
%define SYS_mmap            9
%define SYS_munmap          11
%define SYS_ioctl           16
%define SYS_clock_gettime   228

; ============================================
; File Descriptors
; ============================================
%define STDOUT              1
%define STDERR              2

; ============================================
; ioctl Constants
; ============================================
%define TIOCGWINSZ          0x5413

; ============================================
; mmap Constants
; ============================================
%define PROT_READ           0x1
%define PROT_WRITE          0x2
%define MAP_PRIVATE         0x02
%define MAP_ANONYMOUS       0x20

; ============================================
; clock_gettime Constants
; ============================================
%define CLOCK_MONOTONIC     1

; ============================================
; Time Constants
; ============================================
%define NS_PER_SEC          1000000000
%define NS_PER_MS           1000000
%define MIN_UPDATE_INTERVAL 50000000    ; 50ms in nanoseconds

; ============================================
; Progress Bar Constants
; ============================================
%define RENDER_BUFFER_SIZE  512
%define DEFAULT_TERM_WIDTH  80
%define DEFAULT_BAR_WIDTH   40

; ============================================
; Progress Bar State Structure Offsets
; Structure size: 80 bytes (10 * 8-byte fields)
; ============================================
%define PB_TOTAL            0       ; int64: Total iterations
%define PB_CURRENT          8       ; int64: Current iteration
%define PB_START_TIME       16      ; int64: Start time (ns)
%define PB_LAST_UPDATE      24      ; int64: Last render time (ns)
%define PB_NCOLS            32      ; int64: Terminal width
%define PB_DESC_PTR         40      ; ptr: Description string
%define PB_DESC_LEN         48      ; int64: Description length
%define PB_FLAGS            56      ; uint64: Bit flags
%define PB_BUFFER_PTR       64      ; ptr: Render buffer
%define PB_ALLOC_SIZE       72      ; int64: Total allocated size

%define PROGRESSBAR_SIZE    80

; ============================================
; Flag Bits
; ============================================
%define FLAG_LEAVE          0x01    ; Leave progress bar after completion
%define FLAG_DISABLE        0x02    ; Disable output entirely
%define FLAG_ASCII          0x04    ; Use ASCII characters only
%define FLAG_FIRST_UPDATE   0x08    ; First update (force render)
%define FLAG_CLOSED         0x10    ; Bar has been closed

; ============================================
; ANSI Escape Sequences
; ============================================
%define ANSI_ESC            27      ; Escape character

; ============================================
; Macros
; ============================================

; Save callee-saved registers
%macro PUSH_CALLEE_SAVED 0
    push rbx
    push rbp
    push r12
    push r13
    push r14
    push r15
%endmacro

; Restore callee-saved registers
%macro POP_CALLEE_SAVED 0
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbp
    pop rbx
%endmacro

; Align stack to 16 bytes (required before syscalls/calls)
%macro ALIGN_STACK 1
    sub rsp, %1
%endmacro

%macro UNALIGN_STACK 1
    add rsp, %1
%endmacro
