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
%define SYS_nanosleep       35
%define SYS_clone           56
%define SYS_exit            60
%define SYS_sched_setaffinity 203
%define SYS_sched_getaffinity 204
%define SYS_clock_gettime   228
%define SYS_getcpu          309

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
%define MAP_STACK           0x20000
%define MAP_GROWSDOWN       0x0100

; ============================================
; clone() Flags for Thread Creation
; ============================================
%define CLONE_VM            0x00000100  ; Share memory space
%define CLONE_FS            0x00000200  ; Share filesystem info
%define CLONE_FILES         0x00000400  ; Share file descriptors
%define CLONE_SIGHAND       0x00000800  ; Share signal handlers
%define CLONE_THREAD        0x00010000  ; Same thread group
%define CLONE_PARENT_SETTID 0x00100000  ; Set TID in parent
%define CLONE_CHILD_CLEARTID 0x00200000 ; Clear TID on exit

; Combined flags for creating a thread
%define CLONE_THREAD_FLAGS  (CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND | CLONE_THREAD)

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
%define RENDER_INTERVAL_NS  16666666    ; ~60fps (16.67ms in nanoseconds)
%define THREAD_STACK_SIZE   65536       ; 64KB stack for render thread

; ============================================
; Progress Bar Constants
; ============================================
%define RENDER_BUFFER_SIZE  512
%define DEFAULT_TERM_WIDTH  80
%define DEFAULT_BAR_WIDTH   40

; ============================================
; Progress Bar State Structure Offsets (Sync Mode)
; Structure size: 80 bytes (10 * 8-byte fields)
; ============================================
%define PB_TOTAL            0       ; int64: Total iterations
%define PB_CURRENT          8       ; int64: Current iteration (atomic in async)
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
; Async Progress Bar Extended Structure
; Additional fields after PROGRESSBAR_SIZE
; ============================================
%define PB_RENDER_TID       80      ; int64: Render thread TID
%define PB_STACK_PTR        88      ; ptr: Thread stack base (for munmap)
%define PB_LAST_RENDERED    96      ; int64: Last rendered count (for change detection)
%define PB_PYTHON_CPU       104     ; int64: Python's CPU core
%define PB_RENDER_CPU       112     ; int64: Render thread's CPU core

%define PROGRESSBAR_ASYNC_SIZE  120

; ============================================
; Flag Bits
; ============================================
%define FLAG_LEAVE          0x01    ; Leave progress bar after completion
%define FLAG_DISABLE        0x02    ; Disable output entirely
%define FLAG_ASCII          0x04    ; Use ASCII characters only
%define FLAG_FIRST_UPDATE   0x08    ; First update (force render)
%define FLAG_CLOSED         0x10    ; Bar has been closed
%define FLAG_ASYNC          0x20    ; Async rendering mode enabled
%define FLAG_SHUTDOWN       0x40    ; Signal render thread to shutdown
%define FLAG_THREAD_READY   0x80    ; Render thread is running

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
