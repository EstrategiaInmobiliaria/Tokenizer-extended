#include <stdio.h>

int main() {
    int a, b, suma;
    
    printf("=== SUMA CON CONDICIONAL (C) ===\n");
    printf("Ingresa el primer numero: ");
    scanf("%d", &a);
    printf("Ingresa el segundo numero: ");
    scanf("%d", &b);
    
    suma = a + b;
    printf("La suma es: %d\n", suma);
    
    /* Condicional: si la suma es mayor a 100 */
    if (suma > 100) {
        printf("ALTO\n");
    } else {
        printf("BAJO\n");
    }
    
    return 0;
}
