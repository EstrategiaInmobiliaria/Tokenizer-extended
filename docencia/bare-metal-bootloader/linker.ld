/* Linker Script para Boot Sector */

/* Punto de entrada del programa */
ENTRY(_start)

SECTIONS
{
    /* El BIOS carga el boot sector en 0x7C00 */
    . = 0x7C00;
    
    /* Sección de código */
    .text : {
        *(.text)    /* Todo el código ejecutable */
    }
    
    /* Sección de datos de solo lectura */
    .rodata : {
        *(.rodata)
    }
    
    /* Sección de datos inicializados */
    .data : {
        *(.data)
    }
    
    /* Sección de datos no inicializados (BSS) */
    .bss : {
        *(.bss)
    }
    
    /* Descartar secciones que no necesitamos */
    /DISCARD/ : {
        *(.comment)
        *(.eh_frame)
    }
}
