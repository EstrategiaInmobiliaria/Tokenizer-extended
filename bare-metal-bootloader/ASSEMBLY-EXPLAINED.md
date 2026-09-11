# Explicación Detallada del Código Assembly

Este documento explica **línea por línea** el código del bootloader `boot.s`.

## 🎯 Objetivo

Escribir "Hi!" en verde brillante en la pantalla usando solo Assembly x86, sin sistema operativo.

## 📝 Código Completo Anotado

```asm
# Boot sector assembly completo - Todo en 512 bytes
# El BIOS carga esto en 0x7C00 y salta aquí

.code16                     # Modo real de 16 bits
.global _start

_start:
    # Limpiar segmentos
    xor %ax, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %ss
    mov $0x7C00, %sp

    # Escribir directamente en memoria de video (0xB8000)
    # Modo protegido simple para acceder a 0xB8000
    
    mov $0xB800, %ax        # Segmento de video
    mov %ax, %es            # ES apunta a video
    
    # Escribir 'H' verde en posición 0
    movw $0x0A48, %es:(0)   # 'H' (0x48) + atributo 0x0A (verde)
    
    # Escribir 'i' verde en posición 2
    movw $0x0A69, %es:(2)   # 'i' (0x69) + atributo 0x0A
    
    # Escribir '!' verde en posición 4  
    movw $0x0A21, %es:(4)   # '!' (0x21) + atributo 0x0A

hang:
    hlt
    jmp hang

# Rellenar hasta 510 bytes con 0s
.fill 510 - (. - _start), 1, 0
.byte 0x55
.byte 0xAA
```

## 🔍 Explicación Línea por Línea

### Directivas del Assembler

```asm
.code16
```
**¿Qué hace?** Le dice al assembler que genere código para **modo real de 16 bits**.

**¿Por qué?** Todos los procesadores x86 arrancan en modo real por compatibilidad. Es el modo que usaba el 8086 original (1978).

```asm
.global _start
```
**¿Qué hace?** Exporta el símbolo `_start` para que el linker lo pueda ver.

**¿Por qué?** El linker necesita saber dónde empieza tu código. En `linker.ld` especificamos `ENTRY(_start)`.

---

### Inicialización de Segmentos

```asm
xor %ax, %ax            # ax = 0
```
**¿Qué hace?** Pone el registro AX en 0.

**¿Por qué XOR y no MOV?** 
- `xor %ax, %ax` → 2 bytes de código máquina
- `mov $0, %ax` → 3 bytes de código máquina
- Ahorramos 1 byte (crítico en 512 bytes).

```asm
mov %ax, %ds            # Data Segment = 0
mov %ax, %es            # Extra Segment = 0  
mov %ax, %ss            # Stack Segment = 0
```
**¿Qué hace?** Limpia los segmentos DS, ES y SS (los pone en 0).

**¿Por qué?** El BIOS puede dejar estos registros en cualquier valor. Ponerlos en 0 nos da direcciones predecibles:
- Dirección física = Segmento × 16 + Offset
- Si Segmento = 0, entonces Dirección = Offset (más simple)

```asm
mov $0x7C00, %sp        # Stack Pointer = 0x7C00
```
**¿Qué hace?** Pone el puntero de pila en 0x7C00.

**¿Por qué 0x7C00?** 
- El BIOS carga nuestro código en 0x7C00
- El stack crece **hacia abajo** (de 0x7C00 hacia 0x0000)
- Así el stack no pisa nuestro código

---

### Acceso a Memoria de Video

```asm
mov $0xB800, %ax        # ax = 0xB800
mov %ax, %es            # ES = 0xB800
```
**¿Qué hace?** Pone el segmento ES en 0xB800.

**¿Por qué 0xB800?** 
- Memoria de video VGA en modo texto está en **0xB8000**
- En modo real: Dirección física = Segmento × 16 + Offset
- 0xB800 × 16 = 0xB8000 ✓

**¿Por qué no directamente ES = 0xB8000?**
Los registros de segmento son de 16 bits, no pueden contener 0xB8000 (20 bits).

---

### Escribir en Video

```asm
movw $0x0A48, %es:(0)
```
**¿Qué hace?** Escribe la word (16 bits) `0x0A48` en `ES:0`.

**Desglose:**
- `movw` → Move Word (16 bits)
- `$0x0A48` → Valor inmediato (literal)
- `%es:(0)` → Dirección ES:0 (0xB8000 + 0 = 0xB8000)

**Formato del valor 0x0A48:**
```
High byte: 0x0A = Atributo (verde brillante)
Low byte:  0x48 = 'H' (ASCII 72)
```

**Dirección física:** 0xB8000
- Byte en 0xB8000 = 0x48 = 'H'
- Byte en 0xB8001 = 0x0A = verde brillante

```asm
movw $0x0A69, %es:(2)
```
**Dirección física:** 0xB8002
- Byte en 0xB8002 = 0x69 = 'i'
- Byte en 0xB8003 = 0x0A = verde brillante

```asm
movw $0x0A21, %es:(4)
```
**Dirección física:** 0xB8004
- Byte en 0xB8004 = 0x21 = '!'
- Byte en 0xB8005 = 0x0A = verde brillante

---

### Loop Infinito

```asm
hang:
    hlt
    jmp hang
```
**¿Qué hace?** Detiene el CPU y luego vuelve a `hang`.

**¿Por qué HLT?**
- `hlt` = Halt = Detener CPU hasta próxima interrupción
- Ahorra energía (el CPU no ejecuta instrucciones vacías)

**¿Por qué JMP después de HLT?**
Si llega una interrupción (timer, teclado, etc.), el CPU despierta del `hlt` y ejecuta la siguiente instrucción. El `jmp hang` lo vuelve a dormir.

---

### Firma del Boot Sector

```asm
.fill 510 - (. - _start), 1, 0
```
**¿Qué hace?** Rellena con 0s hasta el byte 510.

**Desglose:**
- `. - _start` → Cuántos bytes llevamos escritos
- `510 - (...)` → Cuántos bytes faltan para llegar a 510
- `, 1, 0` → Repetir el valor 0, de a 1 byte cada vez

**¿Por qué 510?** Porque los últimos 2 bytes (510 y 511) son la firma mágica.

```asm
.byte 0x55
.byte 0xAA
```
**¿Qué hace?** Escribe los bytes 0x55 y 0xAA al final.

**¿Por qué?** 
El BIOS verifica que el sector termine en `0x55 0xAA` para confirmar que es un boot sector válido. Sin esta firma, el BIOS ignora el disco.

---

## 🧮 Aritmética de Direcciones

### Cálculo de Dirección Física en Modo Real

```
Dirección Física = (Segmento << 4) + Offset
                 = (Segmento × 16) + Offset
```

**Ejemplo 1: Video memory**
```
Segmento = 0xB800
Offset   = 0x0000
Física   = (0xB800 × 16) + 0x0000
         = 0xB8000 + 0
         = 0xB8000 ✓
```

**Ejemplo 2: Nuestro código**
```
Segmento = 0x0000 (DS = 0)
Offset   = 0x7C00 (donde el BIOS nos cargó)
Física   = (0x0000 × 16) + 0x7C00
         = 0 + 0x7C00
         = 0x7C00 ✓
```

---

## 🎨 Códigos de Color VGA

El byte de atributo tiene este formato:

```
Bit:  7   6 5 4   3   2 1 0
      │   └─┬─┘   │   └─┬─┘
      │     │     │     └─── Foreground color (0-7)
      │     │     └───────── Foreground bright (0=normal, 1=bright)
      │     └─────────────── Background color (0-7)
      └───────────────────── Background bright / blink
```

**Ejemplo: 0x0A (0000 1010)**
```
0000 → Background negro (0)
1010 → Foreground verde brillante (2 + bright)
```

**Tabla de colores base:**
```
0 = Negro      4 = Rojo
1 = Azul       5 = Magenta
2 = Verde      6 = Marrón/Amarillo
3 = Cian       7 = Blanco
```

**Bit 3 = Bright:**
- 0x02 = Verde oscuro
- 0x0A = Verde brillante (0x02 | 0x08)

---

## 📊 Tamaño del Código

Podemos ver el tamaño de cada sección con `objdump`:

```bash
objdump -h boot_asm.o
```

Para boot.bin completo:
```
Total: 512 bytes exactos
- Código: ~30 bytes
- Padding: ~480 bytes de 0s
- Firma: 2 bytes (0x55 0xAA)
```

---

## 🐛 Debugging

### Ver el desensamblado:

```bash
objdump -D -b binary -m i386 -M intel boot.bin | less
```

Verás algo como:
```asm
0: 31 c0                 xor    eax,eax
2: 8e d8                 mov    ds,eax
4: 8e c0                 mov    es,eax
...
```

### GDB en QEMU:

Terminal 1:
```bash
qemu-system-i386 -drive format=raw,file=boot.bin -s -S
```

Terminal 2:
```bash
gdb
(gdb) target remote :1234
(gdb) break *0x7C00
(gdb) continue
(gdb) stepi              # Ejecutar una instrucción
(gdb) info registers     # Ver registros
(gdb) x/16bx 0xB8000     # Ver memoria de video
```

---

## 🚀 Próximos Pasos

Una vez que domines este bootloader, puedes:

1. **Agregar más texto**
   ```asm
   mov $message, %si
   call print_string
   ```

2. **Leer del teclado**
   ```asm
   mov $0x00, %ah      # Función de BIOS: leer tecla
   int $0x16           # Llamar a BIOS
   ```

3. **Cambiar a modo protegido de 32 bits**
   - Habilita acceso a > 1 MB de RAM
   - Desactiva segmentación
   - Habilita paginación

4. **Cargar un kernel desde disco**
   ```asm
   mov $0x02, %ah      # Función de BIOS: leer sector
   mov $0x01, %al      # Leer 1 sector
   int $0x13           # Llamar a BIOS
   ```

---

## 📚 Recursos

- [Intel 8086 Manual](https://edge.edx.org/c4x/BITSPilani/EEE231/asset/8086_family_Users_Manual_1_.pdf)
- [OSDev Wiki - Bootloaders](https://wiki.osdev.org/Bootloader)
- [VGA Text Mode](https://wiki.osdev.org/Text_mode)
- [x86 Assembly Guide](https://www.cs.virginia.edu/~evans/cs216/guides/x86.html)

---

**Ahora entiendes cada byte que se ejecuta cuando arrancas tu bootloader.** 🚀
