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
