/*
 * Bootloader Bare-Metal con C
 * 
 * NOTA: Esta versión en C está aquí como referencia educativa.
 * La versión actual del bootloader usa solo Assembly (boot.s) 
 * porque es más compacta y cabe en 512 bytes exactos.
 * 
 * Si quieres experimentar con C, necesitarás:
 * 1. Modificar el Makefile para compilar este archivo
 * 2. Ajustar boot.s para llamar a kmain()
 * 3. Probablemente necesitarás un segundo sector (más de 512 bytes)
 */

void kmain(void) {
    // Escribir usando words (16 bits) es más eficiente
    volatile unsigned short *video = (volatile unsigned short*)0xB8000;
    
    /* Formato: byte bajo = ASCII, byte alto = color */
    video[0] = 0x0A48;  // 'H' verde
    video[1] = 0x0A69;  // 'i' verde  
    video[2] = 0x0A21;  // '!' verde
    
    /* Loop infinito */
    while(1) {
        __asm__ volatile("hlt");
    }
}

/*
 * Para usar esta versión C:
 * 
 * 1. Descomentar en boot.s la línea: call kmain
 * 2. Modificar Makefile para compilar boot.c
 * 3. Nota: El binario será >512 bytes, necesitarás multi-sector boot
 */
