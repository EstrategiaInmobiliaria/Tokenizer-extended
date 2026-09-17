# 🚀 Bootloader Bare-Metal - "Hi!" sin Sistema Operativo

Este proyecto demuestra **programación bare-metal**: código que se ejecuta directamente en el hardware sin sistema operativo, sin drivers, sin nada. Tu código **ES** el sistema operativo.

## 🎯 ¿Qué hace este programa?

Muestra **"Hi!"** en verde brillante en la esquina superior izquierda de la pantalla, escribiendo directamente en la memoria de video VGA en `0xB8000`.

**No hay:**
- ❌ Linux/Windows
- ❌ Drivers de video
- ❌ Librería estándar (`printf`, `malloc`)
- ❌ Sistema de archivos

**Solo hay:**
- ✅ Tu código
- ✅ El CPU
- ✅ La memoria de video

## 🧠 Conceptos Clave

### 1. **¿Por qué `volatile`?**

```c
volatile char *video = (volatile char*)0xB8000;
video[0] = 'H';
```

Sin `volatile`, el compilador ve:
```c
video[0] = 'H';  // "Nadie lee esto después"
```

Y **lo elimina** porque cree que es código inútil. Con `volatile` le dices:

> "Escribe SIEMPRE en esta dirección, aunque parezca que nadie lo lee. Hay hardware ahí."

### 2. **Memoria de Video VGA (0xB8000)**

La memoria de video en modo texto VGA está mapeada en `0xB8000`. Cada carácter ocupa **2 bytes**:

```
Byte 0: ASCII del carácter
Byte 1: Atributos de color
```

**Formato de color (byte de atributo):**
```
Bits: FBBB FFFF
      │││  └┬┬┬└─ Color de texto
      │││   └───── F = 1 → texto brillante
      └┴┴───────── Color de fondo
```

**Ejemplo: 0x0A (verde brillante)**
```
0000 1010
││││ ││└┴─ Verde (0xA = 10)
││││ │└─── Brillante activado
└┴┴┴─└──── Fondo negro (0x0)
```

### 3. **Boot Sector (Sector de Arranque)**

El BIOS busca un disco con un **boot sector** válido:
- Exactamente **512 bytes**
- Termina con la firma mágica **`0x55 0xAA`** en los bytes 510 y 511
- El BIOS lo carga en la dirección **`0x7C00`**
- Le pasa el control (salta a `0x7C00`)

Si falta la firma `0x55AA` o el tamaño no es 512 bytes → el BIOS ignora el disco.

### 4. **Triple Fault**

Si tu código hace algo ilegal (acceso inválido a memoria, división por cero, etc.) en bare-metal:
- No hay kernel que capture la excepción
- El CPU entra en **Triple Fault**
- La máquina se reinicia

**En QEMU:** verás la pantalla parpadear y reiniciarse cada ~0.2 segundos.

## 📋 Requisitos

```bash
# Compilador GCC
sudo apt install gcc binutils

# QEMU para emular x86
sudo apt install qemu-system-x86

# Make para automatizar compilación
sudo apt install make
```

## 🔨 Compilar y Ejecutar

### Compilación simple:
```bash
make
```

Salida esperada:
```
===================================
✓ Bootloader compilado: boot.bin
===================================
-rw-r--r-- 1 user user 512 Jan 01 12:00 boot.bin
```

### Ejecutar en QEMU:
```bash
make run
```

Deberías ver:
- Ventana de QEMU con fondo negro
- **"Hi!"** en verde brillante en la esquina superior izquierda
- Nada más (no hay cursor, no hay prompt, no hay OS)

### Comandos útiles:

```bash
make run          # Ejecutar bootloader
make debug        # Ejecutar con GDB (para debugging bajo nivel)
make disasm       # Ver código desensamblado
make clean        # Limpiar archivos de compilación
make rebuild      # Limpiar y recompilar
make info         # Mostrar información del proyecto
```

## 📂 Estructura del Proyecto

```
bare-metal-bootloader/
├── boot.s          # Punto de entrada en Assembly (inicializa CPU)
├── boot.c          # Código principal en C (kmain)
├── linker.ld       # Linker script (dice dónde va cada sección)
├── Makefile        # Automatización de compilación
└── README.md       # Este archivo
```

## 🔍 Explicación Detallada del Código

### boot.s (Assembly)

```asm
.code16                 # Modo real de 16 bits (como arranca x86)
.global _start

_start:
    xor %ax, %ax        # ax = 0
    mov %ax, %ds        # Limpiar segmentos
    mov %ax, %es
    mov %ax, %ss
    mov $0x7C00, %sp    # Stack pointer en 0x7C00
    
    call kmain          # Llamar a función C
    
hang:
    hlt                 # Detener CPU
    jmp hang            # Loop por si despierta

# Rellenar hasta 510 bytes y agregar firma mágica
.fill 510 - (. - _start), 1, 0
.byte 0x55
.byte 0xAA
```

**¿Por qué assembly primero?**
- El CPU arranca en **modo real de 16 bits**
- Necesitamos configurar segmentos, stack, etc.
- Después de la inicialización, saltamos a C

### boot.c (C)

```c
void kmain(void) {
    volatile char *video = (volatile char*)0xB8000;
    
    video[0] = 'H';  // Carácter
    video[1] = 0x0A; // Color (verde)
    video[2] = 'i';
    video[3] = 0x0A;
    video[4] = '!';
    video[5] = 0x0A;
    
    for(;;) {
        __asm__("hlt");  // CPU en idle
    }
}
```

**Detalles importantes:**
- **`volatile`**: Obliga al compilador a escribir en memoria
- **`0xB8000`**: Dirección física de memoria de video
- **Loop infinito**: Sin esto, el CPU ejecuta basura en memoria
- **`hlt`**: Detiene el CPU (ahorra energía, despierta con interrupciones)

### linker.ld (Linker Script)

```ld
ENTRY(_start)

SECTIONS {
    . = 0x7C00;         # Cargar en 0x7C00
    .text : { *(.text) }  # Código
    .data : { *(.data) }  # Datos
    .bss  : { *(.bss)  }  # Variables no inicializadas
}
```

Le dice al linker:
- Punto de entrada: `_start`
- Todo el código va a partir de `0x7C00`
- Orden de secciones: código → datos → bss

## 🎨 Tabla de Colores VGA

| Valor | Color             | Valor | Color                |
|-------|-------------------|-------|----------------------|
| 0x00  | Negro             | 0x08  | Gris oscuro          |
| 0x01  | Azul              | 0x09  | Azul brillante       |
| 0x02  | Verde             | 0x0A  | **Verde brillante**  |
| 0x03  | Cian              | 0x0B  | Cian brillante       |
| 0x04  | Rojo              | 0x0C  | Rojo brillante       |
| 0x05  | Magenta           | 0x0D  | Magenta brillante    |
| 0x06  | Marrón            | 0x0E  | Amarillo             |
| 0x07  | Gris claro        | 0x0F  | Blanco               |

**Para cambiar color de fondo:**
```c
video[1] = 0x1A;  // Verde sobre azul (0x1 = fondo azul, 0xA = verde)
video[1] = 0x4E;  // Amarillo sobre rojo (0x4 = fondo rojo, 0xE = amarillo)
```

## 🐛 Debugging

### Ver código desensamblado:
```bash
make disasm
```

Verás el código máquina real que se ejecuta:
```asm
00007c00 <_start>:
    7c00:   31 c0                   xor    %ax,%ax
    7c02:   8e d8                   mov    %ax,%ds
    ...
```

### Debug con GDB:
```bash
# Terminal 1: Iniciar QEMU en modo debug
make debug

# Terminal 2: Conectar GDB
gdb
(gdb) target remote :1234
(gdb) break *0x7C00
(gdb) continue
```

## 🚧 Errores Comunes

### 1. **QEMU se reinicia constantemente (Triple Fault)**
**Causa:** Tu código accedió a memoria inválida o ejecutó instrucción ilegal.
**Solución:** Verifica punteros, asegúrate que el loop infinito esté presente.

### 2. **No aparece nada en pantalla**
**Causa:** Falta `volatile` o la dirección de memoria es incorrecta.
**Solución:** 
```c
volatile char *video = (volatile char*)0xB8000;  // No olvidar volatile
```

### 3. **"Bootloader no es de 512 bytes"**
**Causa:** El código es muy grande o muy pequeño.
**Solución:** El Makefile automáticamente ajusta el tamaño. Verifica que compile sin errores.

### 4. **QEMU dice "No bootable device"**
**Causa:** Falta la firma mágica `0x55AA`.
**Solución:** El `boot.s` ya la incluye. Si modificaste el código, verifica que esté presente.

## 🎓 Próximos Pasos

Una vez que domines esto, puedes:

1. **Escribir más texto**
   - Llenar toda la pantalla (80x25 caracteres)
   - Crear una función `print_string(char *str)`

2. **Manejar input de teclado**
   - Leer del puerto de teclado (0x60)
   - Mostrar lo que el usuario escribe

3. **Cambiar a modo protegido de 32 bits**
   - Acceder a más de 1MB de RAM
   - Usar paginación de memoria

4. **Cargar un kernel más grande**
   - Leer sectores adicionales del disco
   - Saltar a un kernel en C más complejo

5. **Implementar interrupciones**
   - IDT (Interrupt Descriptor Table)
   - Manejar timer, teclado, etc.

## 📚 Recursos Adicionales

- [OSDev Wiki](https://wiki.osdev.org/) - La Biblia del desarrollo de OS
- [Writing a Simple Operating System from Scratch](https://www.cs.bham.ac.uk/~exr/lectures/opsys/10_11/lectures/os-dev.pdf) - Tutorial completo
- [Intel x86 Manual](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) - Referencia oficial de la arquitectura

## 🏆 La Frontera

> "Del otro lado está el código que mueve el Cheetah del MIT. Del lado de acá, Pascal y `malloc`."

Este bootloader es el primer paso hacia:
- Sistemas operativos
- Firmware embebido
- Control de hardware a bajo nivel
- Robótica avanzada
- Sistemas en tiempo real

**Ya no estás usando el sistema operativo. Tú ERES el sistema operativo.**

---

## 🤝 Contribuciones

Este es un proyecto educativo. Si encuentras formas de mejorarlo o agregar ejemplos, los pull requests son bienvenidos.

## 📄 Licencia

Dominio público. Úsalo para aprender, enseñar, o construir tu propio OS.

---

**Hackea la Matrix. Compila. Rompe cosas. Aprende.** 🖥️✨
