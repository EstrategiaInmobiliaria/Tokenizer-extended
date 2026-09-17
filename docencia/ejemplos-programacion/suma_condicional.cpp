#include <iostream>
using namespace std;

int main() {
    int a, b, suma;
    
    cout << "=== SUMA CON CONDICIONAL (C++) ===" << "\n";
    cout << "Ingresa el primer numero: ";
    cin >> a;
    cout << "Ingresa el segundo numero: ";
    cin >> b;
    
    suma = a + b;
    cout << "La suma es: " << suma << "\n";
    
    // Condicional: si la suma es mayor a 100
    if (suma > 100) {
        cout << "ALTO" << "\n";
    } else {
        cout << "BAJO" << "\n";
    }
    
    return 0;
}
