; SPDX-License-Identifier: Apache-2.0
; Copyright (c) 2026-present Steven Baumann (@SBNovaScript)
; Original repository: https://github.com/SBNovaScript/asmqdm
; See LICENSE and NOTICE in the repository root for details.
; Please retain this header, thank you!

; asmqdm - x86_64 Assembly Progress Bar Library
; ==============================================
; A high-performance progress bar implementation for Python
; using direct Linux syscalls.

%include "constants.inc"

section .data
    ; Static strings for progress bar rendering
    newline:         db 0x0A

section .bss

section .text

; ============================================
; UTILITY FUNCTIONS
; ============================================

; --------------------------------------------
; get_time_ns - Get current monotonic time in nanoseconds
; --------------------------------------------
; Args: none
; Returns: rax = nanoseconds since boot (monotonic)
; --------------------------------------------
global get_time_ns
get_time_ns:
    push rbp
    mov rbp, rsp
    sub rsp, 16                     ; struct timespec (16 bytes)

    ; clock_gettime(CLOCK_MONOTONIC, &ts)
    mov rax, SYS_clock_gettime
    mov rdi, CLOCK_MONOTONIC
    lea rsi, [rbp - 16]
    syscall

    ; Convert to nanoseconds: tv_sec * 1e9 + tv_nsec
    mov rax, [rbp - 16]             ; tv_sec
    mov rcx, NS_PER_SEC
    imul rax, rcx                   ; rax = tv_sec * 1e9
    add rax, [rbp - 8]              ; add tv_nsec

    add rsp, 16
    pop rbp
    ret

; --------------------------------------------
; get_terminal_width - Get terminal width using ioctl
; --------------------------------------------
; Args: none
; Returns: rax = terminal width (default 80 if fails)
; --------------------------------------------
global get_terminal_width
get_terminal_width:
    push rbp
    mov rbp, rsp
    sub rsp, 16                     ; struct winsize (8 bytes, aligned)

    ; ioctl(STDOUT, TIOCGWINSZ, &winsize)
    mov rax, SYS_ioctl
    mov rdi, STDOUT
    mov rsi, TIOCGWINSZ
    lea rdx, [rbp - 16]
    syscall

    ; Check for error
    test rax, rax
    js .default_width

    ; struct winsize { unsigned short ws_row, ws_col, ws_xpixel, ws_ypixel; }
    ; ws_col is at offset 2
    movzx rax, word [rbp - 14]      ; ws_col (offset 2 from start)
    test rax, rax
    jz .default_width
    jmp .done

.default_width:
    mov rax, DEFAULT_TERM_WIDTH

.done:
    add rsp, 16
    pop rbp
    ret

; --------------------------------------------
; int_to_str - Convert unsigned integer to decimal string
; --------------------------------------------
; Args: rdi = buffer pointer (must have space for 20+ chars)
;       rsi = unsigned integer value
; Returns: rax = string length (not including null terminator)
; --------------------------------------------
global int_to_str
int_to_str:
    push rbp
    mov rbp, rsp
    push rbx
    push r12

    mov r12, rdi                    ; Save buffer start
    mov rax, rsi                    ; Value to convert

    ; Handle zero case
    test rax, rax
    jnz .not_zero
    mov byte [rdi], '0'
    mov byte [rdi + 1], 0           ; Null terminator
    mov rax, 1
    jmp .done

.not_zero:
    ; We'll write digits in reverse, then reverse the string
    xor rcx, rcx                    ; Digit count
    mov rbx, 10

.digit_loop:
    test rax, rax
    jz .reverse

    xor rdx, rdx
    div rbx                         ; rax = quotient, rdx = remainder
    add dl, '0'                     ; Convert to ASCII
    mov [rdi + rcx], dl
    inc rcx
    jmp .digit_loop

.reverse:
    ; rcx = number of digits
    ; Now reverse the string in place
    mov r8, rdi                     ; r8 = left pointer
    lea r9, [rdi + rcx - 1]         ; r9 = right pointer

.reverse_loop:
    cmp r8, r9
    jge .reverse_done

    ; Swap bytes at r8 and r9
    mov al, [r8]
    mov bl, [r9]
    mov [r8], bl
    mov [r9], al

    inc r8
    dec r9
    jmp .reverse_loop

.reverse_done:
    mov byte [rdi + rcx], 0         ; Null terminator
    mov rax, rcx                    ; Return length

.done:
    pop r12
    pop rbx
    pop rbp
    ret

; --------------------------------------------
; copy_string - Copy string from source to destination
; --------------------------------------------
; Args: rdi = destination pointer
;       rsi = source pointer
;       rdx = length (bytes to copy)
; Returns: rax = destination + length (pointer to end)
; --------------------------------------------
copy_string:
    mov rcx, rdx
    test rcx, rcx
    jz .copy_done

    ; Use rep movsb for simplicity
    push rdi
    rep movsb
    pop rax
    add rax, rdx
    ret

.copy_done:
    mov rax, rdi
    ret

; --------------------------------------------
; write_stdout - Write buffer to stdout
; --------------------------------------------
; Args: rdi = buffer pointer
;       rsi = length
; Returns: rax = bytes written (or negative on error)
; --------------------------------------------
write_stdout:
    mov rdx, rsi                    ; length
    mov rsi, rdi                    ; buffer
    mov rdi, STDOUT                 ; fd
    mov rax, SYS_write
    syscall
    ret

; --------------------------------------------
; format_time - Format seconds as MM:SS or HH:MM:SS
; --------------------------------------------
; Args: rdi = buffer pointer (needs at least 9 bytes)
;       rsi = total seconds
; Returns: rax = string length
; --------------------------------------------
format_time:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13

    mov r12, rdi                    ; buffer pointer
    mov rax, rsi                    ; total seconds

    ; Calculate hours, minutes, seconds
    xor rdx, rdx
    mov rcx, 3600
    div rcx                         ; rax = hours, rdx = remaining seconds
    mov r8, rax                     ; r8 = hours

    mov rax, rdx
    xor rdx, rdx
    mov rcx, 60
    div rcx                         ; rax = minutes, rdx = seconds
    mov r9, rax                     ; r9 = minutes
    mov r10, rdx                    ; r10 = seconds

    mov rdi, r12                    ; buffer pointer

    ; If hours > 0, format as HH:MM:SS
    test r8, r8
    jz .fmt_no_hours

    ; Format hours
    mov rax, r8
    xor rdx, rdx
    mov rcx, 10
    div rcx
    add al, '0'
    mov [rdi], al
    add dl, '0'
    mov [rdi + 1], dl
    mov byte [rdi + 2], ':'
    add rdi, 3

.fmt_no_hours:
    ; Format minutes
    mov rax, r9
    xor rdx, rdx
    mov rcx, 10
    div rcx
    add al, '0'
    mov [rdi], al
    add dl, '0'
    mov [rdi + 1], dl
    mov byte [rdi + 2], ':'
    add rdi, 3

    ; Format seconds
    mov rax, r10
    xor rdx, rdx
    mov rcx, 10
    div rcx
    add al, '0'
    mov [rdi], al
    add dl, '0'
    mov [rdi + 1], dl
    add rdi, 2

    ; Calculate total length
    mov rax, rdi
    sub rax, r12

    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

; --------------------------------------------
; format_rate - Format iterations per second
; --------------------------------------------
; Args: rdi = buffer pointer
;       rsi = iterations per second (integer)
; Returns: rax = string length written
; --------------------------------------------
format_rate:
    push rbp
    mov rbp, rsp
    push rbx

    mov rbx, rdi                    ; Save buffer start

    ; Convert integer to string
    call int_to_str
    add rdi, rax                    ; Move past the number

    ; Add "it/s"
    mov byte [rdi], 'i'
    mov byte [rdi + 1], 't'
    mov byte [rdi + 2], '/'
    mov byte [rdi + 3], 's'
    add rdi, 4

    ; Return total length
    mov rax, rdi
    sub rax, rbx

    pop rbx
    pop rbp
    ret

; ============================================
; PROGRESS BAR FUNCTIONS
; ============================================

; --------------------------------------------
; progress_bar_create - Create a new progress bar
; --------------------------------------------
; Args: rdi = total iterations
;       rsi = description string pointer (can be NULL)
;       rdx = description length
;       rcx = flags
; Returns: rax = pointer to ProgressBar state (or NULL on error)
; --------------------------------------------
global progress_bar_create
progress_bar_create:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15

    ; Save arguments
    mov r12, rdi                    ; total
    mov r13, rsi                    ; desc_ptr
    mov r14, rdx                    ; desc_len
    mov r15, rcx                    ; flags

    ; Allocate memory using mmap
    ; mmap(NULL, size, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0)
    mov rax, SYS_mmap
    xor rdi, rdi                    ; addr = NULL
    mov rsi, PROGRESSBAR_SIZE + RENDER_BUFFER_SIZE
    mov rdx, PROT_READ | PROT_WRITE
    mov r10, MAP_PRIVATE | MAP_ANONYMOUS
    mov r8, -1                      ; fd = -1
    xor r9, r9                      ; offset = 0
    syscall

    ; Check for error (mmap returns -1 to -4095 on error)
    cmp rax, -4096
    ja .create_alloc_failed

    mov rbx, rax                    ; Save pointer to state

    ; Initialize structure fields
    mov qword [rbx + PB_TOTAL], r12
    mov qword [rbx + PB_CURRENT], 0

    ; Get start time
    call get_time_ns
    mov [rbx + PB_START_TIME], rax
    mov qword [rbx + PB_LAST_UPDATE], 0     ; Force first render

    ; Get terminal width
    call get_terminal_width
    mov [rbx + PB_NCOLS], rax

    ; Store description
    mov qword [rbx + PB_DESC_PTR], r13
    mov qword [rbx + PB_DESC_LEN], r14

    ; Store flags (add FLAG_FIRST_UPDATE to force first render)
    or r15, FLAG_FIRST_UPDATE
    mov qword [rbx + PB_FLAGS], r15

    ; Set buffer pointer (after the struct)
    lea rax, [rbx + PROGRESSBAR_SIZE]
    mov [rbx + PB_BUFFER_PTR], rax

    ; Store allocation size
    mov qword [rbx + PB_ALLOC_SIZE], PROGRESSBAR_SIZE + RENDER_BUFFER_SIZE

    ; Return state pointer
    mov rax, rbx
    jmp .create_done

.create_alloc_failed:
    xor rax, rax                    ; Return NULL

.create_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

; --------------------------------------------
; progress_bar_update - Update progress bar
; --------------------------------------------
; Args: rdi = ProgressBar* state
;       rsi = increment (usually 1)
; Returns: rax = current count
; --------------------------------------------
global progress_bar_update
progress_bar_update:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13

    mov rbx, rdi                    ; Save state pointer
    mov r12, rsi                    ; Save increment

    ; Check if disabled
    mov rax, [rbx + PB_FLAGS]
    test rax, FLAG_DISABLE
    jnz .update_return_current

    ; Update current count
    add qword [rbx + PB_CURRENT], r12

    ; Check if this is the first update (force render)
    mov rax, [rbx + PB_FLAGS]
    test rax, FLAG_FIRST_UPDATE
    jnz .update_force_render

    ; Check if enough time has passed since last render
    call get_time_ns
    mov r13, rax                    ; Current time

    mov rcx, [rbx + PB_LAST_UPDATE]
    sub rax, rcx
    cmp rax, MIN_UPDATE_INTERVAL
    jl .update_return_current

.update_force_render:
    ; Clear first update flag
    and qword [rbx + PB_FLAGS], ~FLAG_FIRST_UPDATE

    ; Render progress bar
    mov rdi, rbx
    call progress_bar_render

.update_return_current:
    mov rax, [rbx + PB_CURRENT]

    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

; --------------------------------------------
; progress_bar_render - Render progress bar to stdout
; --------------------------------------------
; Args: rdi = ProgressBar* state
; Returns: nothing
; --------------------------------------------
global progress_bar_render
progress_bar_render:
    push rbp
    mov rbp, rsp
    sub rsp, 64                     ; Local variables
    push rbx
    push r12
    push r13
    push r14
    push r15

    mov rbx, rdi                    ; State pointer
    mov r12, [rbx + PB_BUFFER_PTR]  ; Buffer pointer
    mov r13, r12                    ; Current write position

    ; --- Start building output string ---

    ; Write carriage return to go back to start of line
    mov byte [r13], 0x0D
    inc r13

    ; Add description if present
    mov rsi, [rbx + PB_DESC_PTR]
    test rsi, rsi
    jz .render_no_desc

    mov rcx, [rbx + PB_DESC_LEN]
    test rcx, rcx
    jz .render_no_desc

    ; Copy description
    mov rdi, r13
    mov rdx, rcx
    call copy_string
    mov r13, rax

    ; Add ": "
    mov byte [r13], ':'
    mov byte [r13 + 1], ' '
    add r13, 2

.render_no_desc:
    ; Calculate percentage: (current * 100) / total
    mov rax, [rbx + PB_CURRENT]
    mov rcx, 100
    imul rax, rcx
    mov rcx, [rbx + PB_TOTAL]
    test rcx, rcx
    jz .render_zero_percent
    xor rdx, rdx
    div rcx
    jmp .render_got_percent
.render_zero_percent:
    xor rax, rax
.render_got_percent:
    mov r14, rax                    ; r14 = percentage (0-100)

    ; Clamp percentage to 100
    cmp r14, 100
    jle .render_percent_ok
    mov r14, 100
.render_percent_ok:

    ; Write percentage number
    mov rdi, r13
    mov rsi, r14
    call int_to_str
    add r13, rax

    ; Add "%|"
    mov byte [r13], '%'
    mov byte [r13 + 1], '|'
    add r13, 2

    ; Calculate bar width
    ; Available width = ncols - desc_len - overhead (~35 chars for counters)
    mov rax, [rbx + PB_NCOLS]
    sub rax, [rbx + PB_DESC_LEN]
    sub rax, 40                     ; Overhead for numbers, brackets, etc.

    ; Clamp bar width between 10 and 50
    cmp rax, 10
    jge .render_bar_min_ok
    mov rax, 10
.render_bar_min_ok:
    cmp rax, 50
    jle .render_bar_max_ok
    mov rax, 50
.render_bar_max_ok:
    mov r15, rax                    ; r15 = bar width

    ; Calculate filled portion: (percentage * bar_width) / 100
    mov rax, r14
    imul rax, r15
    mov rcx, 100
    xor rdx, rdx
    div rcx
    ; rax = filled count

    ; Draw filled portion
    mov rcx, rax
    mov r8, rcx                     ; Save filled count
.render_fill_loop:
    test rcx, rcx
    jz .render_fill_done
    mov byte [r13], '#'
    inc r13
    dec rcx
    jmp .render_fill_loop
.render_fill_done:

    ; Draw empty portion
    mov rcx, r15
    sub rcx, r8                     ; empty = bar_width - filled
.render_empty_loop:
    test rcx, rcx
    jz .render_empty_done
    mov byte [r13], '-'
    inc r13
    dec rcx
    jmp .render_empty_loop
.render_empty_done:

    ; Add "| "
    mov byte [r13], '|'
    mov byte [r13 + 1], ' '
    add r13, 2

    ; Add current/total
    mov rdi, r13
    mov rsi, [rbx + PB_CURRENT]
    call int_to_str
    add r13, rax

    mov byte [r13], '/'
    inc r13

    mov rdi, r13
    mov rsi, [rbx + PB_TOTAL]
    call int_to_str
    add r13, rax

    ; Add " ["
    mov byte [r13], ' '
    mov byte [r13 + 1], '['
    add r13, 2

    ; Calculate elapsed time in seconds and update last_update
    call get_time_ns
    mov [rbx + PB_LAST_UPDATE], rax

    ; Get elapsed
    mov rcx, [rbx + PB_START_TIME]
    sub rax, rcx

    ; Convert to seconds
    mov rcx, NS_PER_SEC
    xor rdx, rdx
    div rcx                         ; rax = elapsed seconds
    mov [rbp - 8], rax              ; Store elapsed seconds

    ; Format elapsed time
    mov rdi, r13
    mov rsi, rax
    call format_time
    add r13, rax

    ; Add "<" for remaining time
    mov byte [r13], '<'
    inc r13

    ; Calculate remaining time (ETA)
    ; remaining = elapsed * (total - current) / current
    mov rax, [rbx + PB_CURRENT]
    test rax, rax
    jz .render_unknown_eta

    mov rcx, [rbx + PB_TOTAL]
    sub rcx, rax                    ; remaining iterations
    jle .render_unknown_eta         ; If current >= total, ETA = 0

    mov rax, [rbp - 8]              ; elapsed seconds
    imul rax, rcx                   ; elapsed * remaining_iterations
    mov rcx, [rbx + PB_CURRENT]
    xor rdx, rdx
    div rcx                         ; eta_seconds
    jmp .render_format_eta

.render_unknown_eta:
    xor rax, rax                    ; ETA = 0
.render_format_eta:
    mov rdi, r13
    mov rsi, rax
    call format_time
    add r13, rax

    ; Add ", "
    mov byte [r13], ','
    mov byte [r13 + 1], ' '
    add r13, 2

    ; Calculate rate (iterations per second)
    mov rax, [rbp - 8]              ; elapsed seconds
    test rax, rax
    jz .render_rate_zero

    mov rcx, [rbx + PB_CURRENT]
    xchg rax, rcx                   ; rax = current, rcx = elapsed
    xor rdx, rdx
    div rcx                         ; rate = current / elapsed
    jmp .render_format_rate

.render_rate_zero:
    xor rax, rax
.render_format_rate:
    mov rdi, r13
    mov rsi, rax
    call format_rate
    add r13, rax

    ; Add "]"
    mov byte [r13], ']'
    inc r13

    ; Calculate total output length
    mov rsi, r13
    sub rsi, r12                    ; length = end - start

    ; Write to stdout
    mov rdi, r12
    call write_stdout

    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    add rsp, 64
    pop rbp
    ret

; --------------------------------------------
; progress_bar_close - Close and cleanup progress bar
; --------------------------------------------
; Args: rdi = ProgressBar* state
; Returns: nothing
; --------------------------------------------
global progress_bar_close
progress_bar_close:
    push rbp
    mov rbp, rsp
    push rbx

    mov rbx, rdi                    ; Save state pointer

    ; Check if NULL
    test rbx, rbx
    jz .close_done

    ; Check if already closed
    mov rax, [rbx + PB_FLAGS]
    test rax, FLAG_CLOSED
    jnz .close_done

    ; Check if disabled
    test rax, FLAG_DISABLE
    jnz .close_skip_final_render

    ; Force final render
    mov rdi, rbx
    call progress_bar_render

    ; Check leave flag - if set, print newline
    mov rax, [rbx + PB_FLAGS]
    test rax, FLAG_LEAVE
    jz .close_skip_final_render

    ; Print newline
    lea rdi, [rel newline]
    mov rsi, 1
    call write_stdout

.close_skip_final_render:
    ; Mark as closed
    or qword [rbx + PB_FLAGS], FLAG_CLOSED

    ; Free memory using munmap
    mov rax, SYS_munmap
    mov rdi, rbx
    mov rsi, [rbx + PB_ALLOC_SIZE]
    syscall

.close_done:
    pop rbx
    pop rbp
    ret

; --------------------------------------------
; progress_bar_set_description - Update description
; --------------------------------------------
; Args: rdi = ProgressBar* state
;       rsi = new description pointer
;       rdx = new description length
; Returns: nothing
; --------------------------------------------
global progress_bar_set_description
progress_bar_set_description:
    mov [rdi + PB_DESC_PTR], rsi
    mov [rdi + PB_DESC_LEN], rdx
    ret

; ============================================
; ASYNC RENDERING FUNCTIONS
; ============================================

; --------------------------------------------
; get_current_cpu - Get current CPU core number
; --------------------------------------------
; Args: none
; Returns: rax = CPU number (0-based)
; --------------------------------------------
get_current_cpu:
    push rbp
    mov rbp, rsp
    sub rsp, 16

    ; getcpu(cpu*, node*, unused)
    mov rax, SYS_getcpu
    lea rdi, [rbp - 8]          ; cpu output
    xor rsi, rsi                ; node (don't care)
    xor rdx, rdx                ; unused
    syscall

    mov eax, [rbp - 8]          ; Return CPU number

    add rsp, 16
    pop rbp
    ret

; --------------------------------------------
; set_cpu_affinity - Set CPU affinity for current thread
; --------------------------------------------
; Args: rdi = CPU mask (bitmask of allowed CPUs)
; Returns: rax = 0 on success, negative on error
; --------------------------------------------
set_cpu_affinity:
    push rbp
    mov rbp, rsp
    sub rsp, 16

    ; Store the mask on stack
    mov [rbp - 8], rdi

    ; sched_setaffinity(0, sizeof(mask), &mask)
    ; tid=0 means current thread
    mov rax, SYS_sched_setaffinity
    xor rdi, rdi                ; tid = 0 (current thread)
    mov rsi, 8                  ; sizeof(cpu_set_t) - using 8 bytes
    lea rdx, [rbp - 8]          ; pointer to mask
    syscall

    add rsp, 16
    pop rbp
    ret

; --------------------------------------------
; nanosleep_ms - Sleep for specified milliseconds
; --------------------------------------------
; Args: rdi = milliseconds to sleep
; Returns: nothing
; --------------------------------------------
nanosleep_ms:
    push rbp
    mov rbp, rsp
    sub rsp, 32                 ; struct timespec * 2

    ; Convert ms to timespec
    mov rax, rdi
    xor rdx, rdx
    mov rcx, 1000
    div rcx                     ; rax = seconds, rdx = remaining ms

    mov [rbp - 32], rax         ; tv_sec
    imul rdx, NS_PER_MS
    mov [rbp - 24], rdx         ; tv_nsec

    ; nanosleep(&req, &rem)
    mov rax, SYS_nanosleep
    lea rdi, [rbp - 32]         ; req
    lea rsi, [rbp - 16]         ; rem (unused)
    syscall

    add rsp, 32
    pop rbp
    ret

; --------------------------------------------
; render_thread_main - Main loop for async render thread
; --------------------------------------------
; Entry point for the child thread after clone()
; rbx must contain the state pointer when jumping here
; --------------------------------------------
render_thread_main:
    ; Signal that thread is ready
    or qword [rbx + PB_FLAGS], FLAG_THREAD_READY

.render_loop:
    ; Check for shutdown signal
    mov rax, [rbx + PB_FLAGS]
    test rax, FLAG_SHUTDOWN
    jnz .shutdown

    ; Sleep for render interval (~16ms for 60fps)
    mov rdi, 16                 ; 16ms
    call nanosleep_ms

    ; Check shutdown again after sleep
    mov rax, [rbx + PB_FLAGS]
    test rax, FLAG_SHUTDOWN
    jnz .shutdown

    ; Atomic read of current count
    mov rax, [rbx + PB_CURRENT]

    ; Check if count changed since last render
    cmp rax, [rbx + PB_LAST_RENDERED]
    je .render_loop             ; No change, skip render

    ; Render progress bar
    mov rdi, rbx
    call progress_bar_render

    ; Update last rendered count
    mov rax, [rbx + PB_CURRENT]
    mov [rbx + PB_LAST_RENDERED], rax

    jmp .render_loop

.shutdown:
    ; Exit thread
    mov rax, SYS_exit
    xor rdi, rdi                ; exit code 0
    syscall
    ; Never returns

; --------------------------------------------
; progress_bar_create_async - Create async progress bar
; --------------------------------------------
; Args: rdi = total iterations
;       rsi = description string pointer (can be NULL)
;       rdx = description length
;       rcx = flags (FLAG_ASYNC should be set)
; Returns: rax = pointer to ProgressBar state (or NULL on error)
; --------------------------------------------
global progress_bar_create_async
progress_bar_create_async:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15

    ; Save arguments
    mov r12, rdi                    ; total
    mov r13, rsi                    ; desc_ptr
    mov r14, rdx                    ; desc_len
    mov r15, rcx                    ; flags

    ; Ensure FLAG_ASYNC is set
    or r15, FLAG_ASYNC

    ; Allocate memory for state + buffer
    mov rax, SYS_mmap
    xor rdi, rdi                    ; addr = NULL
    mov rsi, PROGRESSBAR_ASYNC_SIZE + RENDER_BUFFER_SIZE
    mov rdx, PROT_READ | PROT_WRITE
    mov r10, MAP_PRIVATE | MAP_ANONYMOUS
    mov r8, -1
    xor r9, r9
    syscall

    cmp rax, -4096
    ja .async_alloc_failed

    mov rbx, rax                    ; Save state pointer

    ; Initialize base structure fields (same as sync)
    mov qword [rbx + PB_TOTAL], r12
    mov qword [rbx + PB_CURRENT], 0

    call get_time_ns
    mov [rbx + PB_START_TIME], rax
    mov qword [rbx + PB_LAST_UPDATE], 0

    call get_terminal_width
    mov [rbx + PB_NCOLS], rax

    mov qword [rbx + PB_DESC_PTR], r13
    mov qword [rbx + PB_DESC_LEN], r14

    or r15, FLAG_FIRST_UPDATE
    mov qword [rbx + PB_FLAGS], r15

    lea rax, [rbx + PROGRESSBAR_ASYNC_SIZE]
    mov [rbx + PB_BUFFER_PTR], rax

    mov qword [rbx + PB_ALLOC_SIZE], PROGRESSBAR_ASYNC_SIZE + RENDER_BUFFER_SIZE

    ; Initialize async-specific fields
    mov qword [rbx + PB_LAST_RENDERED], 0

    ; Get Python's current CPU
    call get_current_cpu
    mov [rbx + PB_PYTHON_CPU], rax
    mov r12, rax                    ; Save Python's CPU

    ; Allocate stack for render thread
    mov rax, SYS_mmap
    xor rdi, rdi
    mov rsi, THREAD_STACK_SIZE
    mov rdx, PROT_READ | PROT_WRITE
    mov r10, MAP_PRIVATE | MAP_ANONYMOUS | MAP_STACK
    mov r8, -1
    xor r9, r9
    syscall

    cmp rax, -4096
    ja .async_stack_failed

    mov [rbx + PB_STACK_PTR], rax   ; Save stack base for cleanup

    ; Calculate stack top (stack grows down, needs 16-byte alignment)
    add rax, THREAD_STACK_SIZE
    and rax, ~0xF                   ; Align to 16 bytes
    sub rax, 8                      ; Make room for "return address" alignment
    mov r13, rax                    ; r13 = stack top

    ; Store state pointer at a known location on the child's stack
    ; Child will find it at [rsp] after clone
    sub r13, 8
    mov [r13], rbx                  ; State pointer for child to find

    ; Create render thread using clone
    ; After clone: parent has rax=child_pid, child has rax=0
    ; Both continue from the instruction after syscall
    mov rax, SYS_clone
    mov rdi, CLONE_THREAD_FLAGS
    mov rsi, r13                    ; Stack for new thread
    xor rdx, rdx                    ; parent_tid
    xor r10, r10                    ; child_tid
    xor r8, r8                      ; tls
    syscall

    ; Check if we're the parent or child
    test rax, rax
    jz .child_thread                ; rax=0 means we're the child
    js .async_clone_failed          ; rax<0 means error

    ; Parent continues here
    mov [rbx + PB_RENDER_TID], rax
    jmp .parent_continues

.child_thread:
    ; Child thread: retrieve state pointer and jump to render loop
    ; The state pointer is at [rsp] (we set it up before clone)
    pop rbx                         ; rbx = state pointer
    jmp render_thread_main          ; Jump to the render loop

.parent_continues:

    ; Set CPU affinity for render thread (exclude Python's core)
    ; Build mask with all CPUs except Python's
    mov rax, -1                     ; All bits set
    mov rcx, r12                    ; Python's CPU
    btr rax, rcx                    ; Clear Python's CPU bit

    ; Only set affinity if we have more than 1 CPU
    cmp rcx, 0
    je .skip_affinity               ; Single CPU, skip

    mov rdi, rax
    call set_cpu_affinity

.skip_affinity:
    ; Wait for thread to be ready (simple spin)
    mov rcx, 1000000                ; Max iterations
.wait_ready:
    mov rax, [rbx + PB_FLAGS]
    test rax, FLAG_THREAD_READY
    jnz .thread_ready
    dec rcx
    jnz .wait_ready
    ; Thread didn't start in time, but continue anyway

.thread_ready:
    ; Return state pointer
    mov rax, rbx
    jmp .async_done

.async_clone_failed:
    ; Cleanup stack
    mov rax, SYS_munmap
    mov rdi, [rbx + PB_STACK_PTR]
    mov rsi, THREAD_STACK_SIZE
    syscall

.async_stack_failed:
    ; Cleanup state
    mov rax, SYS_munmap
    mov rdi, rbx
    mov rsi, PROGRESSBAR_ASYNC_SIZE + RENDER_BUFFER_SIZE
    syscall

.async_alloc_failed:
    xor rax, rax                    ; Return NULL

.async_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

; --------------------------------------------
; progress_bar_update_async - Atomic update (lock-free)
; --------------------------------------------
; Args: rdi = ProgressBar* state
;       rsi = increment (usually 1)
; Returns: rax = new current count
; --------------------------------------------
global progress_bar_update_async
progress_bar_update_async:
    ; Atomic increment - this is the entire hot path!
    lock xadd qword [rdi + PB_CURRENT], rsi
    add rax, rsi                    ; xadd returns OLD value, add increment
    ret

; --------------------------------------------
; progress_bar_close_async - Close async progress bar
; --------------------------------------------
; Args: rdi = ProgressBar* state
; Returns: nothing
; --------------------------------------------
global progress_bar_close_async
progress_bar_close_async:
    push rbp
    mov rbp, rsp
    push rbx
    push r12

    mov rbx, rdi

    ; Check if NULL
    test rbx, rbx
    jz .close_async_done

    ; Check if already closed
    mov rax, [rbx + PB_FLAGS]
    test rax, FLAG_CLOSED
    jnz .close_async_done

    ; Signal shutdown to render thread
    or qword [rbx + PB_FLAGS], FLAG_SHUTDOWN

    ; Wait for thread to exit (simple delay)
    ; In production, would use futex for proper synchronization
    mov rdi, 50                     ; 50ms should be enough
    call nanosleep_ms

    ; Final render (sync)
    mov rax, [rbx + PB_FLAGS]
    test rax, FLAG_DISABLE
    jnz .skip_async_final

    mov rdi, rbx
    call progress_bar_render

    ; Print newline if leave flag set
    mov rax, [rbx + PB_FLAGS]
    test rax, FLAG_LEAVE
    jz .skip_async_final

    lea rdi, [rel newline]
    mov rsi, 1
    call write_stdout

.skip_async_final:
    ; Mark as closed
    or qword [rbx + PB_FLAGS], FLAG_CLOSED

    ; Cleanup thread stack
    mov rax, SYS_munmap
    mov rdi, [rbx + PB_STACK_PTR]
    mov rsi, THREAD_STACK_SIZE
    syscall

    ; Cleanup state
    mov rax, SYS_munmap
    mov rdi, rbx
    mov rsi, [rbx + PB_ALLOC_SIZE]
    syscall

.close_async_done:
    pop r12
    pop rbx
    pop rbp
    ret
