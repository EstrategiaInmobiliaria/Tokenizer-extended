# Makefile para Bootloader Bare-Metal (Assembly puro)

AS = as
LD = ld

ASFLAGS = --32
LDFLAGS = -m elf_i386 -T linker.ld --oformat binary

BOOT_ASM = boot.s
BOOT_BIN = boot.bin
BOOT_OBJ = boot_asm.o

# Target principal
all: $(BOOT_BIN)
	@echo "==================================="
	@echo "✓ Bootloader compilado: $(BOOT_BIN)"
	@echo "==================================="
	@ls -lh $(BOOT_BIN)
	@echo ""
	@echo "Para ejecutar:"
	@echo "  make run"

# Ensamblar
boot_asm.o: $(BOOT_ASM)
	$(AS) $(ASFLAGS) $< -o $@

# Linkear
$(BOOT_BIN): boot_asm.o
	$(LD) $(LDFLAGS) $< -o $@
	@size=$$(stat -c%s $(BOOT_BIN) 2>/dev/null || stat -f%z $(BOOT_BIN) 2>/dev/null); \
	if [ "$$size" -eq 512 ]; then \
		echo "✓ Tamaño correcto: 512 bytes"; \
	else \
		echo "⚠ Tamaño: $$size bytes (esperado 512)"; \
		exit 1; \
	fi

# Ejecutar en QEMU
run: $(BOOT_BIN)
	@echo "Iniciando QEMU... (Ctrl+C o cierra la ventana para salir)"
	qemu-system-i386 -drive format=raw,file=$(BOOT_BIN)

# Limpiar
clean:
	rm -f $(BOOT_OBJ) $(BOOT_BIN)
	@echo "✓ Limpieza completa"

rebuild: clean all

.PHONY: all run clean rebuild
