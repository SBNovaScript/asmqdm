# asmqdm Makefile
# Build x86_64 assembly progress bar library

# Tools
NASM = nasm
LD = ld
PYTHON = python3

# Directories
SRC_DIR = src/asm
PYTHON_DIR = src/python/asmqdm
BUILD_DIR = build

# Files
ASM_SOURCES = $(wildcard $(SRC_DIR)/*.asm)
ASM_OBJECTS = $(patsubst $(SRC_DIR)/%.asm,$(BUILD_DIR)/%.o,$(ASM_SOURCES))
LIBRARY = $(BUILD_DIR)/libasmqdm.so

# Flags
NASMFLAGS = -f elf64 -g -F dwarf -I $(SRC_DIR)/include/
LDFLAGS = -shared

# Default target
all: $(LIBRARY)

# Create build directory
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Assemble .asm files to .o files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.asm $(SRC_DIR)/include/*.inc | $(BUILD_DIR)
	$(NASM) $(NASMFLAGS) -o $@ $<

# Link shared library
$(LIBRARY): $(ASM_OBJECTS)
	$(LD) $(LDFLAGS) -o $@ $^

# Copy library to Python package
install-lib: $(LIBRARY)
	cp $(LIBRARY) $(PYTHON_DIR)/

# Install Python package in development mode
install: install-lib
	$(PYTHON) -m pip install -e .

# Run tests
test: install-lib
	$(PYTHON) -m pytest tests/ -v

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR)
	rm -f $(PYTHON_DIR)/libasmqdm.so

# Debug build
debug: NASMFLAGS += -g -F dwarf
debug: all

# Disassemble for inspection
disasm: $(LIBRARY)
	objdump -d -M intel $(LIBRARY)

# Show symbols
symbols: $(LIBRARY)
	nm $(LIBRARY)

.PHONY: all install install-lib test clean debug disasm symbols
