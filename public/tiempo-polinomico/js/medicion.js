/**
 * Motor de medición: cronometra los algoritmos del catálogo con `performance.now()`
 * sobre tamaños de entrada crecientes.
 *
 * Detalles que hacen que la medida sea honesta y no bloquee la pestaña:
 *  - Calentamiento previo, para que el compilador JIT ya haya optimizado el bucle.
 *  - Repeticiones adaptativas: si una ejecución es demasiado rápida para el reloj,
 *    se repite muchas veces y se divide el total.
 *  - Se toma el mejor de varias muestras (el ruido del sistema solo puede añadir tiempo).
 *  - Antes de pasar al tamaño siguiente se estima cuánto costaría; si supera el
 *    presupuesto, la serie se detiene. Eso es exactamente "la pared exponencial".
 */
(function (global) {
  "use strict";

  const TP = (global.TP = global.TP || {});
  const utiles = TP.utiles;

  function cronometrar(algoritmo, caso, repeticiones) {
    let acumulado = 0;
    const inicio = performance.now();
    for (let i = 0; i < repeticiones; i++)
      acumulado += algoritmo.ejecutar(caso);
    const fin = performance.now();
    TP.sumidero += acumulado;
    return fin - inicio;
  }

  async function medirPunto(algoritmo, n, configuracion) {
    const caso = algoritmo.preparar(n);
    await utiles.cederControl();

    TP.sumidero += algoritmo.ejecutar(caso); // calentamiento

    let repeticiones = Math.max(1, algoritmo.repeticionesBase || 1);
    let msTotal = cronometrar(algoritmo, caso, repeticiones);

    // Sube las repeticiones hasta que el reloj tenga algo decente que medir.
    while (
      msTotal < configuracion.tiempoObjetivoMs &&
      msTotal * 2 < configuracion.presupuestoMs &&
      repeticiones < 1 << 26
    ) {
      repeticiones *= 2;
      await utiles.cederControl();
      msTotal = cronometrar(algoritmo, caso, repeticiones);
    }

    let mejorPorEjecucion = msTotal / repeticiones;
    for (let muestra = 1; muestra < configuracion.muestras; muestra++) {
      await utiles.cederControl();
      const tiempo = cronometrar(algoritmo, caso, repeticiones);
      mejorPorEjecucion = Math.min(mejorPorEjecucion, tiempo / repeticiones);
    }

    const operaciones = algoritmo.operaciones(n);
    return {
      n: n,
      repeticiones: repeticiones,
      msPorEjecucion: mejorPorEjecucion,
      msTotal: mejorPorEjecucion * repeticiones,
      operaciones: operaciones,
      nsPorOperacion: (mejorPorEjecucion * 1e6) / operaciones,
    };
  }

  /**
   * Mide una serie completa de tamaños para un algoritmo.
   * `opciones.alPunto(punto, algoritmo)` se llama tras cada medida, para que la
   * interfaz pueda dibujar en directo.
   */
  async function medirSerie(algoritmo, opciones) {
    const configuracion = Object.assign(
      { presupuestoMs: 400, tiempoObjetivoMs: 25, muestras: 3 },
      opciones || {},
    );
    const puntos = [];
    let muro = null;

    for (let indice = 0; indice < algoritmo.tamanos.length; indice++) {
      const n = algoritmo.tamanos[indice];

      if (configuracion.cancelado && configuracion.cancelado()) break;

      // ¿Merece la pena intentarlo? Se extrapola con el modelo teórico.
      if (puntos.length > 0) {
        const anterior = puntos[puntos.length - 1];
        const factor =
          algoritmo.operaciones(n) / Math.max(1, anterior.operaciones);
        const estimacionMs = anterior.msPorEjecucion * factor;
        if (estimacionMs > configuracion.presupuestoMs) {
          muro = { n: n, estimacionMs: estimacionMs };
          break;
        }
      }

      if (configuracion.alEmpezarPunto) {
        configuracion.alEmpezarPunto(n, algoritmo, indice);
      }
      await utiles.cederControl();

      const punto = await medirPunto(algoritmo, n, configuracion);
      puntos.push(punto);
      if (configuracion.alPunto) configuracion.alPunto(punto, algoritmo);
      await utiles.siguienteCuadro();
    }

    return { algoritmo: algoritmo, puntos: puntos, muro: muro };
  }

  /**
   * Estadísticas didácticas de una serie:
   *  - cómo se multiplica el tiempo al pasar de un tamaño al siguiente,
   *  - el exponente empírico k que sale de ajustar log t frente a log n,
   *  - el coste por operación, que debe quedarse casi constante si el modelo acierta.
   */
  function estadisticas(serie) {
    const puntos = serie.puntos;
    const saltos = [];
    for (let i = 1; i < puntos.length; i++) {
      const anterior = puntos[i - 1];
      const actual = puntos[i];
      saltos.push({
        deN: anterior.n,
        aN: actual.n,
        factorN: actual.n / anterior.n,
        factorTiempo: actual.msPorEjecucion / anterior.msPorEjecucion,
        factorTeorico:
          serie.algoritmo.operaciones(actual.n) /
          serie.algoritmo.operaciones(anterior.n),
      });
    }

    let exponente = null;
    if (puntos.length >= 2) {
      let sumaX = 0;
      let sumaY = 0;
      let sumaXY = 0;
      let sumaXX = 0;
      puntos.forEach(function (punto) {
        const x = Math.log(punto.n);
        const y = Math.log(punto.msPorEjecucion);
        sumaX += x;
        sumaY += y;
        sumaXY += x * y;
        sumaXX += x * x;
      });
      const cantidad = puntos.length;
      const denominador = cantidad * sumaXX - sumaX * sumaX;
      if (Math.abs(denominador) > 1e-12) {
        exponente = (cantidad * sumaXY - sumaX * sumaY) / denominador;
      }
    }

    const nsPorOperacion = puntos.length
      ? puntos[puntos.length - 1].nsPorOperacion
      : null;

    return {
      saltos: saltos,
      exponenteEmpirico: exponente,
      nsPorOperacion: nsPorOperacion,
      operacionesPorSegundo: nsPorOperacion ? 1e9 / nsPorOperacion : null,
    };
  }

  TP.medicion = {
    medirSerie: medirSerie,
    medirPunto: medirPunto,
    estadisticas: estadisticas,
  };
})(window);
