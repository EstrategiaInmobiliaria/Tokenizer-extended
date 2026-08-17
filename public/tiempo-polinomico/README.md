# Laboratorio visual: ¿qué es el tiempo polinómico?

Aplicación interactiva en español para **entender y explicar** el tiempo polinómico
con mediciones de tiempo reales, gráficas animadas y simulaciones en movimiento.

No necesita instalación, ni conexión a internet, ni servidor: es HTML, CSS y
JavaScript sin dependencias.

## Cómo abrirla

- **En clase, sin nada más**: abre `index.html` haciendo doble clic (o arrástralo a
  una ventana del navegador). Funciona igual desde un USB o desde una carpeta
  compartida.
- **Servida por el proyecto**: con el servidor de Next.js en marcha, está en
  `/tiempo-polinomico/index.html`.
- **Servida a mano** (útil para proyectar desde otro equipo de la red):

```bash
cd public/tiempo-polinomico
python3 -m http.server 8000
# después, abre http://localhost:8000/
```

Requiere un navegador reciente (Chrome, Edge, Firefox o Safari de los últimos
años). El botón **Modo presentación** agranda toda la tipografía para que se lea
desde el fondo del aula.

## Qué hay en cada sección

1. **La idea clave.** La definición `T(n) ≤ c·n^k` con un mando para cambiar `n` y
   un botón «Duplicar n». Cada fila muestra las operaciones necesarias y, sobre
   todo, **por cuánto se multiplica el trabajo al duplicar la entrada**: ×2 en
   lineal, ×4 en cuadrático, ×8 en cúbico… y un número impensable en exponencial.
2. **Mide tiempos reales.** Ejecuta algoritmos de verdad en el ordenador de clase
   (búsqueda binaria, búsqueda lineal, ordenación por mezcla, burbuja,
   multiplicación de matrices, subconjuntos por fuerza bruta y permutaciones) y los
   cronometra con `performance.now()`. Dibuja la gráfica en directo, rellena una
   tabla con la columna decisiva («tiempo × …») y redacta las conclusiones con el
   exponente `k` que sale de esas medidas.
3. **Carrera a escala real.** Todos los carriles resuelven el mismo problema de
   tamaño `n` con la velocidad medida en el paso anterior. El reloj marca tiempo de
   máquina y la pantalla indica siempre cuánto lo está acelerando la animación.
4. **La pared exponencial.** Extrapolación a unidades humanas (segundos, días,
   años, edades del universo) y la tabla «¿hasta qué tamaño puedo llegar?» con el
   mayor `n` que cabe en un segundo, un minuto, una hora, un día y un año.
5. **Paso a paso.** Dos algoritmos animados sobre la misma lista y a la misma
   velocidad de comparaciones por segundo, para ver de dónde sale el `n²`. Debajo,
   la duplicación exponencial: cada objeto nuevo dobla las combinaciones.
6. **Guion para clase.** Secuencia de unos 20 minutos, frases que funcionan,
   errores frecuentes que conviene desmontar y la definición para el cuaderno.

## Atajos de teclado

| Tecla     | Acción                            |
| --------- | --------------------------------- |
| `1` … `6` | Salta a cada sección              |
| `P`       | Modo presentación                 |
| `M`       | Lanza la medición del laboratorio |
| `Espacio` | Arranca o pausa la carrera        |

## Cómo se mide (para responder en clase «¿esto es de verdad?»)

- Cada tamaño se mide varias veces y se **conserva el mejor tiempo**: el ruido del
  sistema operativo solo puede añadir tiempo, nunca quitarlo.
- Si una ejecución es más rápida que la resolución del reloj, se **repite muchas
  veces y se divide** el total entre el número de repeticiones.
- Hay un **calentamiento** previo para que el compilador del navegador ya haya
  optimizado el bucle cuando empieza la medición.
- El resultado de cada algoritmo se acumula en una variable global para que el
  motor de JavaScript **no pueda eliminar el cálculo** por considerarlo inútil.
- Antes de pasar al tamaño siguiente se estima su coste; si supera el presupuesto
  elegido, la serie se detiene y se anuncia. Esa parada **es** la pared exponencial,
  y conviene leerla en voz alta.

Como los tiempos se miden en el ordenador que tengas delante, las cifras cambian de
un equipo a otro (y son más lentas dentro de una máquina virtual). Esa variación es
parte de la lección: lo que **no** cambia es cómo crecen.

## Estructura de los archivos

```
tiempo-polinomico/
├── index.html          estructura y textos de las seis secciones
├── estilos.css         tema oscuro de alto contraste, pensado para proyector
└── js/
    ├── utiles.js       formateo de tiempos y cantidades, ayudas de animación
    ├── algoritmos.js   catálogo de algoritmos reales y sus modelos de coste
    ├── medicion.js     motor de cronometraje y estadísticas didácticas
    ├── grafica.js      gráfica animada en canvas con curva teórica
    ├── carrera.js      carrera de carriles con reloj de máquina
    ├── pasoapaso.js    visor de comparaciones y duplicación exponencial
    ├── escalado.js     barras logarítmicas y tabla de límites
    └── app.js          conexión de controles, atajos y estado compartido
```
