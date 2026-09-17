# Anatomía del Bootloader (Hexdump Completo)

Este archivo muestra el contenido completo del `boot.bin` en formato hexadecimal, con anotaciones explicando cada parte.

## 📊 Hexdump Completo con Anotaciones

```
Offset   Hex                                          ASCII          Descripción
─────────────────────────────────────────────────────────────────────────────────
00000000  31 c0 8e d8 8e c0 8e d0  bc 00 7c b8 00 b8 8e c0  |1.........|.....|
          ───── ───── ───── ─────  ─────── ───────── ─────
            │     │     │     │        │        │       └─── mov %ax, %es (ES = 0xB800)
            │     │     │     │        │        └─────────── mov $0xB800, %ax
            │     │     │     │        └──────────────────── mov $0x7C00, %sp
            │     │     │     └───────────────────────────── mov %ax, %ss (SS = 0)
            │     │     └─────────────────────────────────── mov %ax, %es (ES = 0)
            │     └───────────────────────────────────────── mov %ax, %ds (DS = 0)
            └─────────────────────────────────────────────── xor %ax, %ax (AX = 0)

00000010  26 c7 06 00 00 48 0a 26  c7 06 02 00 69 0a 26 c7  |&....H.&....i.&.|
          ────────────────────────  ────────────────────────
                    │                          │             
                    │                          └─────────────── movw $0x0A69, %es:(2) 'i' verde
                    └────────────────────────────────────────── movw $0x0A48, %es:(0) 'H' verde
                    
00000020  06 04 00 21 0a f4 eb fd  00 00 00 00 00 00 00 00  |...!............|
          ──────────────── ── ────
                 │         │   └───────────────────────────── jmp hang (salto a HLT)
                 │         └───────────────────────────────── hlt (detener CPU)
                 └─────────────────────────────────────────── movw $0x0A21, %es:(4) '!' verde

00000030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
          ← Padding con ceros (relleno hasta byte 510) →
*
          ... (460 líneas idénticas de 0x00 omitidas) ...
*
000001f0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 55 aa  |..............U.|
                                                      ───────
                                                         └───── 0x55 0xAA (firma mágica)

00000200
```

## 🔍 Análisis por Secciones

### Sección 1: Inicialización (bytes 0x00 - 0x0D)
```
31 c0        xor    %ax, %ax          ; AX = 0
8e d8        mov    %ax, %ds          ; DS = 0
8e c0        mov    %ax, %es          ; ES = 0 (temporal)
8e d0        mov    %ax, %ss          ; SS = 0
bc 00 7c     mov    $0x7C00, %sp      ; SP = 0x7C00 (stack pointer)
b8 00 b8     mov    $0xB800, %ax      ; AX = 0xB800
8e c0        mov    %ax, %es          ; ES = 0xB800 (segmento de video)
```

**Tamaño:** 14 bytes  
**Propósito:** Configurar segmentos y preparar acceso a video

---

### Sección 2: Escritura en Video (bytes 0x0E - 0x27)
```
26 c7 06 00 00 48 0a    movw   $0x0A48, %es:(0)    ; 'H' verde en posición 0
26 c7 06 02 00 69 0a    movw   $0x0A69, %es:(2)    ; 'i' verde en posición 2
26 c7 06 04 00 21 0a    movw   $0x0A21, %es:(4)    ; '!' verde en posición 4
```

**Tamaño:** 21 bytes (7 bytes × 3 caracteres)  
**Propósito:** Escribir "Hi!" en pantalla

**Desglose de `movw $0x0A48, %es:(0)`:**
```
26           Prefijo de segmento ES:
c7 06        Opcode de MOV [immediate word to memory]
00 00        Offset 0 (little-endian)
48 0a        Valor 0x0A48 (little-endian: byte bajo primero)
             0x48 = 'H', 0x0A = verde brillante
```

---

### Sección 3: Loop Infinito (bytes 0x28 - 0x29)
```
f4           hlt                       ; Detener CPU
eb fd        jmp    hang (-3 bytes)   ; Saltar a HLT
```

**Tamaño:** 2 bytes  
**Propósito:** Mantener el CPU detenido (no ejecutar basura)

**Cálculo del salto:**
- `eb` = JMP short (salto relativo de 1 byte)
- `fd` = -3 en complemento a 2
- Dirección actual: 0x29
- Salto: 0x29 + 2 (tamaño instrucción) - 3 = 0x28 (dirección del HLT)

---

### Sección 4: Padding (bytes 0x2A - 0x1FD)
```
00 00 00 ... (468 bytes)
```

**Tamaño:** 468 bytes  
**Propósito:** Rellenar hasta llegar al byte 510

**Cálculo:**
```
Código real: 30 bytes (0x00 - 0x1D)
Padding:     480 bytes (0x1E - 0x1FD)
Firma:       2 bytes (0x1FE - 0x1FF)
Total:       512 bytes
```

---

### Sección 5: Firma Mágica (bytes 0x1FE - 0x1FF)
```
55 aa        0x55 0xAA (magic signature)
```

**Tamaño:** 2 bytes  
**Propósito:** Identificar boot sector válido para el BIOS

**Little-endian:**
- Byte 510 (0x1FE): 0x55
- Byte 511 (0x1FF): 0xAA
- El BIOS busca la word 0xAA55 en posición 510

---

## 📏 Distribución de Espacio

```
┌─────────────────────────────────────────┐
│  Código ejecutable (30 bytes)          │ 0x00 - 0x1D
│  - Init: 14 bytes                       │
│  - Video: 21 bytes                      │
│  - Loop: 2 bytes                        │
├─────────────────────────────────────────┤
│  Padding con 0x00 (480 bytes)          │ 0x1E - 0x1FD
│                                         │
│  (Espacio disponible para más código)   │
│                                         │
├─────────────────────────────────────────┤
│  Firma mágica 0x55 0xAA (2 bytes)      │ 0x1FE - 0x1FF
└─────────────────────────────────────────┘
Total: 512 bytes
```

---

## 🎯 Optimización del Código

### ¿Por qué es tan pequeño?

1. **XOR en vez de MOV para poner en 0:**
   ```
   xor %ax, %ax     ; 2 bytes
   vs
   mov $0, %ax      ; 3 bytes
   ```

2. **Escribir words en vez de bytes:**
   ```
   movw $0x0A48, %es:(0)    ; 7 bytes (carácter + color)
   vs
   movb $0x48, %es:(0)      ; 6 bytes
   movb $0x0A, %es:(1)      ; 6 bytes = 12 bytes total
   ```
   La versión word es más compacta.

3. **JMP short en vez de JMP near:**
   ```
   jmp hang         ; 2 bytes (eb fd)
   vs
   jmp 0x7C28       ; 5 bytes (e9 xx xx)
   ```

### Espacio disponible

```
512 bytes totales
- 30 bytes de código
- 2 bytes de firma
= 480 bytes libres para expandir
```

Puedes agregar hasta **480 bytes más** de código antes de necesitar un segundo sector.

---

## 🧮 Verificación Manual

### Calcular checksum:
```bash
cksum boot.bin
```

### Ver solo el código (sin padding):
```bash
hexdump -C boot.bin | head -5
```

### Ver solo la firma:
```bash
tail -c 2 boot.bin | hexdump -C
# Debe mostrar: 55 aa
```

### Contar bytes de padding:
```bash
# Contar cuántos 0x00 hay
hexdump -v boot.bin | grep "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" | wc -l
# Resultado: 30 líneas × 16 bytes = 480 bytes de padding
```

---

## 🔬 Comparación: ¿Qué pasaría con más código?

Si quisieras escribir un mensaje más largo, por ejemplo **"Hello, World!"** (13 caracteres):

```
Código actual:  30 bytes
Mensaje nuevo:  91 bytes (7 bytes × 13 caracteres)
Loop:           2 bytes
Total:          93 bytes

Espacio usado: 93 / 512 = 18.16%
```

Todavía cabrías cómodamente en 512 bytes.

---

## 🚀 ¿Qué sigue?

Si llenas los 512 bytes, necesitas:

1. **Cargar un segundo sector:**
   ```asm
   mov $0x02, %ah      ; Función BIOS: leer sector
   mov $0x01, %al      ; Leer 1 sector adicional
   mov $0x00, %ch      ; Cilindro 0
   mov $0x02, %cl      ; Sector 2
   mov $0x00, %dh      ; Cabeza 0
   int $0x13           ; Llamar a BIOS
   ```

2. **Usar el segundo sector para tu código principal:**
   - Boot sector (512 bytes): Solo carga el sector 2
   - Sector 2 (512+ bytes): Tu código real

Así funcionan bootloaders reales como GRUB.

---

## 📚 Recursos para Profundizar

- [x86 Opcode Reference](http://ref.x86asm.net/)
- [VGA Hardware](https://wiki.osdev.org/VGA_Hardware)
- [BIOS Interrupts](https://en.wikipedia.org/wiki/BIOS_interrupt_call)
- [Boot Sequence](https://wiki.osdev.org/Boot_Sequence)

---

**Ahora puedes leer el hexdump y entender cada byte.** 🔍
