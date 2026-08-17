/**
 * Catálogo de algoritmos reales que se cronometran en el navegador.
 *
 * Cada entrada describe una clase de complejidad y trae una implementación de
 * verdad (no una simulación): `preparar(n)` construye los datos y `ejecutar(datos)`
 * hace el trabajo devolviendo un valor que se acumula fuera para que el motor de
 * JavaScript no pueda eliminar el cálculo por considerarlo inútil.
 */
(function (global) {
  "use strict";

  const TP = (global.TP = global.TP || {});

  /** Sumidero global: evita que el JIT elimine bucles cuyo resultado no se usa. */
  TP.sumidero = 0;

  function generadorPseudoaleatorio(semilla) {
    let estado = semilla >>> 0 || 123456789;
    return function siguiente() {
      estado ^= estado << 13;
      estado >>>= 0;
      estado ^= estado >>> 17;
      estado ^= estado << 5;
      estado >>>= 0;
      return estado / 4294967296;
    };
  }

  function enterosAleatorios(n, maximo, semilla) {
    const aleatorio = generadorPseudoaleatorio(semilla || n + 7);
    const datos = new Int32Array(n);
    for (let i = 0; i < n; i++) datos[i] = Math.floor(aleatorio() * maximo);
    return datos;
  }

  function enterosOrdenados(n) {
    const datos = new Int32Array(n);
    for (let i = 0; i < n; i++) datos[i] = i * 2;
    return datos;
  }

  function decimalesAleatorios(n, semilla) {
    const aleatorio = generadorPseudoaleatorio(semilla || n + 13);
    const datos = new Float64Array(n);
    for (let i = 0; i < n; i++) datos[i] = aleatorio();
    return datos;
  }

  function potenciasDeDos(desde, hasta) {
    const lista = [];
    for (let v = desde; v <= hasta; v *= 2) lista.push(v);
    return lista;
  }

  function factorial(n) {
    let total = 1;
    for (let i = 2; i <= n; i++) total *= i;
    return total;
  }

  const ALGORITMOS = [
    {
      id: "constante",
      nombre: "Acceso directo a un dato",
      clase: "O(1)",
      etiqueta: "constante",
      familia: "polinomica",
      exponente: 0,
      color: "#94a3b8",
      resumen:
        "Leer la posición central de una lista. Da igual que la lista tenga mil o un millón de elementos: siempre es un salto.",
      cambioN: "×2",
      operaciones: function () {
        return 1;
      },
      invertir: function () {
        return Infinity;
      },
      log10Operaciones: function () {
        return 0;
      },
      tamanos: potenciasDeDos(1024, 4194304),
      repeticionesBase: 4096,
      preparar: function (n) {
        return { datos: enterosAleatorios(n, 1000000, 99), n: n };
      },
      ejecutar: function (caso) {
        const datos = caso.datos;
        return datos[caso.n >> 1] + datos[0] + datos[caso.n - 1];
      },
    },
    {
      id: "logaritmica",
      nombre: "Búsqueda binaria",
      clase: "O(log n)",
      etiqueta: "logarítmica",
      familia: "polinomica",
      exponente: 0,
      color: "#22d3ee",
      resumen:
        "Buscar en una lista ordenada partiendo el problema por la mitad. Al doblar el tamaño solo hace UNA comparación más.",
      cambioN: "×2",
      operaciones: function (n) {
        return Math.max(1, Math.log2(n));
      },
      invertir: function (operaciones) {
        return Math.pow(2, Math.min(operaciones, 4096));
      },
      log10Operaciones: function (n) {
        return Math.log10(Math.max(1, Math.log2(n)));
      },
      tamanos: potenciasDeDos(4096, 4194304),
      repeticionesBase: 512,
      preparar: function (n) {
        return { datos: enterosOrdenados(n), n: n, objetivo: (n - 1) * 2 };
      },
      ejecutar: function (caso) {
        const datos = caso.datos;
        let inicio = 0;
        let fin = caso.n - 1;
        let encontrado = -1;
        while (inicio <= fin) {
          const medio = (inicio + fin) >> 1;
          const valor = datos[medio];
          if (valor === caso.objetivo) {
            encontrado = medio;
            break;
          }
          if (valor < caso.objetivo) inicio = medio + 1;
          else fin = medio - 1;
        }
        return encontrado;
      },
    },
    {
      id: "lineal",
      nombre: "Búsqueda lineal",
      clase: "O(n)",
      etiqueta: "lineal",
      familia: "polinomica",
      exponente: 1,
      color: "#4ade80",
      resumen:
        "Recorrer la lista entera comparando uno a uno. Al doblar el tamaño, tarda el doble. Es el patrón más intuitivo.",
      cambioN: "×2",
      operaciones: function (n) {
        return n;
      },
      invertir: function (operaciones) {
        return operaciones;
      },
      log10Operaciones: function (n) {
        return Math.log10(n);
      },
      tamanos: potenciasDeDos(16384, 8388608),
      repeticionesBase: 1,
      preparar: function (n) {
        return { datos: enterosAleatorios(n, 1000000, 5), n: n, objetivo: -1 };
      },
      ejecutar: function (caso) {
        const datos = caso.datos;
        const n = caso.n;
        let encontrado = -1;
        for (let i = 0; i < n; i++) {
          if (datos[i] === caso.objetivo) {
            encontrado = i;
            break;
          }
        }
        return encontrado + datos[n - 1];
      },
    },
    {
      id: "nlogn",
      nombre: "Ordenación por mezcla",
      clase: "O(n log n)",
      etiqueta: "casi lineal",
      familia: "polinomica",
      exponente: 1,
      color: "#a3e635",
      resumen:
        "Ordenar dividiendo y mezclando (merge sort). Es el coste típico de ordenar bien: un poco más que lineal.",
      cambioN: "×2",
      operaciones: function (n) {
        return n * Math.max(1, Math.log2(n));
      },
      invertir: function (operaciones) {
        // n·log₂n no se puede despejar a mano: se busca por bisección.
        let bajo = 1;
        let alto = 2;
        while (alto * Math.log2(alto) < operaciones && alto < 1e18) alto *= 2;
        for (let i = 0; i < 80; i++) {
          const medio = (bajo + alto) / 2;
          if (medio * Math.max(1, Math.log2(medio)) < operaciones) bajo = medio;
          else alto = medio;
        }
        return bajo;
      },
      log10Operaciones: function (n) {
        return Math.log10(n) + Math.log10(Math.max(1, Math.log2(n)));
      },
      tamanos: potenciasDeDos(4096, 1048576),
      repeticionesBase: 1,
      preparar: function (n) {
        return {
          origen: decimalesAleatorios(n, 21),
          trabajo: new Float64Array(n),
          auxiliar: new Float64Array(n),
          n: n,
        };
      },
      ejecutar: function (caso) {
        const trabajo = caso.trabajo;
        const auxiliar = caso.auxiliar;
        const n = caso.n;
        trabajo.set(caso.origen);
        for (let ancho = 1; ancho < n; ancho *= 2) {
          for (let inicio = 0; inicio < n; inicio += ancho * 2) {
            const medio = Math.min(inicio + ancho, n);
            const fin = Math.min(inicio + ancho * 2, n);
            let i = inicio;
            let j = medio;
            for (let k = inicio; k < fin; k++) {
              if (i < medio && (j >= fin || trabajo[i] <= trabajo[j])) {
                auxiliar[k] = trabajo[i++];
              } else {
                auxiliar[k] = trabajo[j++];
              }
            }
          }
          for (let k = 0; k < n; k++) trabajo[k] = auxiliar[k];
        }
        return trabajo[n >> 1];
      },
    },
    {
      id: "cuadratica",
      nombre: "Ordenación por burbuja",
      clase: "O(n²)",
      etiqueta: "cuadrática",
      familia: "polinomica",
      exponente: 2,
      color: "#fbbf24",
      resumen:
        "Comparar cada elemento con todos los demás. Al doblar el tamaño tarda CUATRO veces más: 2² = 4.",
      cambioN: "×2",
      operaciones: function (n) {
        return (n * (n - 1)) / 2;
      },
      invertir: function (operaciones) {
        return (1 + Math.sqrt(1 + 8 * operaciones)) / 2;
      },
      log10Operaciones: function (n) {
        return (
          Math.log10(Math.max(1, n)) +
          Math.log10(Math.max(1, n - 1)) -
          Math.log10(2)
        );
      },
      // Se para en 8000: más allá, el tamaño supera la caché del procesador y el
      // tiempo crece más de lo que dice el modelo, lo que despistaría en clase.
      tamanos: [500, 1000, 2000, 4000, 8000],
      repeticionesBase: 1,
      preparar: function (n) {
        return {
          origen: decimalesAleatorios(n, 33),
          trabajo: new Float64Array(n),
          n: n,
        };
      },
      ejecutar: function (caso) {
        const lista = caso.trabajo;
        const n = caso.n;
        lista.set(caso.origen);
        for (let i = 0; i < n - 1; i++) {
          for (let j = 0; j < n - 1 - i; j++) {
            const a = lista[j];
            const b = lista[j + 1];
            if (a > b) {
              lista[j] = b;
              lista[j + 1] = a;
            }
          }
        }
        return lista[0];
      },
    },
    {
      id: "cubica",
      nombre: "Multiplicación de matrices",
      clase: "O(n³)",
      etiqueta: "cúbica",
      familia: "polinomica",
      exponente: 3,
      color: "#fb923c",
      resumen:
        "Multiplicar dos matrices n×n con el método clásico. Al doblar n tarda OCHO veces más: 2³ = 8. Sigue siendo polinómico.",
      cambioN: "×2",
      operaciones: function (n) {
        return n * n * n;
      },
      invertir: function (operaciones) {
        return Math.cbrt(operaciones);
      },
      log10Operaciones: function (n) {
        return 3 * Math.log10(n);
      },
      tamanos: [16, 32, 64, 128, 256],
      repeticionesBase: 1,
      preparar: function (n) {
        return {
          a: decimalesAleatorios(n * n, 41),
          b: decimalesAleatorios(n * n, 43),
          c: new Float64Array(n * n),
          n: n,
        };
      },
      ejecutar: function (caso) {
        const a = caso.a;
        const b = caso.b;
        const c = caso.c;
        const n = caso.n;
        for (let i = 0; i < n; i++) {
          const filaA = i * n;
          for (let j = 0; j < n; j++) {
            let suma = 0;
            for (let k = 0; k < n; k++) suma += a[filaA + k] * b[k * n + j];
            c[filaA + j] = suma;
          }
        }
        return c[n * n - 1];
      },
    },
    {
      id: "exponencial",
      nombre: "Subconjuntos por fuerza bruta",
      clase: "O(2ⁿ)",
      etiqueta: "exponencial",
      familia: "exponencial",
      exponente: null,
      color: "#f43f5e",
      resumen:
        "Probar todas las combinaciones posibles de n objetos para ver si alguna suma exacta. Cada objeto nuevo DUPLICA el trabajo.",
      cambioN: "+2",
      operaciones: function (n) {
        return Math.pow(2, n);
      },
      invertir: function (operaciones) {
        return Math.log2(Math.max(1, operaciones));
      },
      log10Operaciones: function (n) {
        return n * Math.log10(2);
      },
      tamanos: [10, 12, 14, 16, 18, 20, 22, 24, 26, 28],
      repeticionesBase: 1,
      preparar: function (n) {
        const pesos = enterosAleatorios(n, 500, 61);
        let objetivo = 0;
        for (let i = 0; i < n; i += 3) objetivo += pesos[i];
        return {
          pesos: pesos,
          n: n,
          objetivo: objetivo + 1,
          pertenece: new Uint8Array(n),
        };
      },
      // Recorre los 2ⁿ subconjuntos en orden de Gray: cada paso solo mete o saca
      // un elemento, así que el número de operaciones es exactamente 2ⁿ.
      ejecutar: function (caso) {
        const pesos = caso.pesos;
        const pertenece = caso.pertenece;
        const total = Math.pow(2, caso.n);
        const objetivo = caso.objetivo;
        pertenece.fill(0);
        let suma = 0;
        let mejor = 0;
        for (let paso = 1; paso < total; paso++) {
          let bit = 0;
          let resto = paso;
          while ((resto & 1) === 0) {
            resto >>= 1;
            bit += 1;
          }
          if (pertenece[bit]) {
            pertenece[bit] = 0;
            suma -= pesos[bit];
          } else {
            pertenece[bit] = 1;
            suma += pesos[bit];
          }
          if (suma <= objetivo && suma > mejor) mejor = suma;
        }
        return mejor;
      },
    },
    {
      id: "factorial",
      nombre: "Rutas del viajante (permutaciones)",
      clase: "O(n!)",
      etiqueta: "factorial",
      familia: "exponencial",
      exponente: null,
      color: "#e879f9",
      resumen:
        "Probar todos los órdenes posibles de visita de n ciudades. Cada ciudad nueva multiplica el trabajo por n.",
      cambioN: "+1",
      operaciones: function (n) {
        return factorial(n);
      },
      invertir: function (operaciones) {
        let n = 1;
        while (factorial(n + 1) <= operaciones && n < 200) n += 1;
        return n;
      },
      log10Operaciones: function (n) {
        return TP.utiles.log10Factorial(n);
      },
      tamanos: [5, 6, 7, 8, 9, 10, 11, 12, 13],
      repeticionesBase: 1,
      preparar: function (n) {
        const coordenadas = decimalesAleatorios(n * 2, 77);
        const distancias = new Float64Array(n * n);
        for (let i = 0; i < n; i++) {
          for (let j = 0; j < n; j++) {
            const dx = coordenadas[i * 2] - coordenadas[j * 2];
            const dy = coordenadas[i * 2 + 1] - coordenadas[j * 2 + 1];
            distancias[i * n + j] = Math.sqrt(dx * dx + dy * dy);
          }
        }
        return {
          distancias: distancias,
          n: n,
          orden: new Int32Array(n),
          contadores: new Int32Array(n),
        };
      },
      // Permutaciones por el algoritmo de Heap en versión iterativa:
      // recorre las n! rutas midiendo la longitud de cada una.
      ejecutar: function (caso) {
        const n = caso.n;
        const distancias = caso.distancias;
        const orden = caso.orden;
        const contadores = caso.contadores;
        for (let i = 0; i < n; i++) {
          orden[i] = i;
          contadores[i] = 0;
        }
        let mejor = Infinity;
        let longitud = 0;
        for (let i = 1; i < n; i++) {
          longitud += distancias[orden[i - 1] * n + orden[i]];
        }
        if (longitud < mejor) mejor = longitud;

        let i = 0;
        while (i < n) {
          if (contadores[i] < i) {
            const j = i % 2 === 0 ? 0 : contadores[i];
            const temporal = orden[j];
            orden[j] = orden[i];
            orden[i] = temporal;

            longitud = 0;
            for (let k = 1; k < n; k++) {
              longitud += distancias[orden[k - 1] * n + orden[k]];
            }
            if (longitud < mejor) mejor = longitud;

            contadores[i] += 1;
            i = 0;
          } else {
            contadores[i] = 0;
            i += 1;
          }
        }
        return mejor;
      },
    },
  ];

  const porId = {};
  ALGORITMOS.forEach(function (algoritmo) {
    porId[algoritmo.id] = algoritmo;
  });

  TP.ALGORITMOS = ALGORITMOS;
  TP.algoritmo = function (id) {
    return porId[id];
  };
  TP.factorial = factorial;
})(window);
