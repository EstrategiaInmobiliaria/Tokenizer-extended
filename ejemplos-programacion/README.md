# Ejemplos de Programación: Pascal vs C vs C++

Este directorio contiene ejemplos comparativos de los mismos programas escritos en Pascal, C y C++.

## 📚 Diferencias Clave

### 1. Entrada/Salida
| Pascal | C | C++ |
|--------|---|-----|
| `readln(a);` | `scanf("%d", &a);` | `cin >> a;` |
| `writeln('Texto');` | `printf("Texto\n");` | `cout << "Texto" << "\n";` |

**Nota importante en C:** El `&` antes de la variable en `scanf` es crucial. Sin él, el programa crashea.

### 2. Bloques de código
- **Pascal:** `begin ... end;`
- **C/C++:** `{ ... }`

### 3. Asignación vs Comparación
- **Pascal:** `:=` (asignar), `=` (comparar)
- **C/C++:** `=` (asignar), `==` (comparar)

**Error clásico:** `if (a = 5)` asigna 5 a `a` (no compara). Siempre usa `if (a == 5)`.

### 4. Condicionales
**Pascal:**
```pascal
if suma > 100 then
  writeln('ALTO')
else
  writeln('BAJO');
```

**C:**
```c
if (suma > 100) {
    printf("ALTO\n");
} else {
    printf("BAJO\n");
}
```

**C++:**
```cpp
if (suma > 100) {
    cout << "ALTO" << "\n";
} else {
    cout << "BAJO" << "\n";
}
```

**Diferencias en condicionales:**
- Pascal: `then` después de la condición, sin paréntesis
- C/C++: Condición entre paréntesis `()`, sin `then`, bloques con llaves `{}`

## 🛠️ Compilar y Ejecutar

### Para C:
```bash
gcc suma_condicional.c -o suma_condicional_c
./suma_condicional_c
```

### Para C++:
```bash
g++ suma_condicional.cpp -o suma_condicional_cpp
./suma_condicional_cpp
```

### Para Pascal (si tienes Free Pascal Compiler):
```bash
fpc suma_condicional.pas
./suma_condicional
```

## 🎯 Ejemplos de Prueba

**Caso 1: Suma BAJA**
- Entrada: `a = 30`, `b = 40`
- Resultado: `suma = 70`, muestra `BAJO`

**Caso 2: Suma ALTA**
- Entrada: `a = 80`, `b = 50`
- Resultado: `suma = 130`, muestra `ALTO`

**Caso 3: Suma en el límite**
- Entrada: `a = 50`, `b = 50`
- Resultado: `suma = 100`, muestra `BAJO` (porque 100 NO es mayor que 100)

## 📂 Navegación en Terminal

- `cd ejemplos-programacion` - Entrar a esta carpeta
- `cd ..` - Subir un nivel
- `ls` - Ver archivos en la carpeta actual
- `pwd` - Ver en qué carpeta estás
