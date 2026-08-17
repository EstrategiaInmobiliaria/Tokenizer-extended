/**
 * Utilidades compartidas: formateo de tiempos y números en lenguaje humano,
 * más pequeños ayudantes de animación y de DOM.
 */
(function (global) {
  "use strict";

  const TP = (global.TP = global.TP || {});

  const SEGUNDOS_POR_ANO = 31557600; // año juliano
  const EDAD_UNIVERSO_ANOS = 13.8e9;

  function redondear(valor, decimales) {
    if (!isFinite(valor)) return String(valor);
    const absoluto = Math.abs(valor);
    let cifras = decimales;
    if (cifras == null) cifras = absoluto >= 100 ? 0 : absoluto >= 10 ? 1 : 2;
    return valor.toLocaleString("es-ES", {
      minimumFractionDigits: 0,
      maximumFractionDigits: cifras,
    });
  }

  /** Convierte un número de segundos en algo que una persona pueda imaginar. */
  function formatearTiempo(segundos) {
    if (!isFinite(segundos)) return "infinito";
    if (segundos <= 0) return "0 s";
    if (segundos < 1e-6) return redondear(segundos * 1e9) + " ns";
    if (segundos < 1e-3) return redondear(segundos * 1e6) + " µs";
    if (segundos < 1) return redondear(segundos * 1e3) + " ms";
    if (segundos < 90) return redondear(segundos) + " s";
    if (segundos < 5400) return redondear(segundos / 60) + " min";
    if (segundos < 172800) return redondear(segundos / 3600) + " horas";
    if (segundos < SEGUNDOS_POR_ANO)
      return redondear(segundos / 86400) + " días";

    const anos = segundos / SEGUNDOS_POR_ANO;
    if (anos < 1000) return redondear(anos) + " años";
    if (anos < 1e6) return redondear(anos / 1e3) + " mil años";
    if (anos < 1e9) return redondear(anos / 1e6) + " millones de años";
    const universos = anos / EDAD_UNIVERSO_ANOS;
    if (universos < 1) return redondear(anos / 1e9) + " mil millones de años";
    if (universos < 1e6) return redondear(universos) + "× la edad del universo";
    return notacionCientifica(anos) + " años";
  }

  function notacionCientifica(valor) {
    if (!isFinite(valor)) return "∞";
    if (valor === 0) return "0";
    const exponente = Math.floor(Math.log10(Math.abs(valor)));
    const mantisa = valor / Math.pow(10, exponente);
    return redondear(mantisa, 1) + "·10^" + exponente;
  }

  /** Números grandes: 1.2 millones, 3.4 billones, 10^42… */
  function formatearCantidad(valor) {
    if (!isFinite(valor)) return "∞";
    const absoluto = Math.abs(valor);
    if (absoluto < 1000) return redondear(valor);
    if (absoluto < 1e6) return redondear(valor / 1e3) + " mil";
    if (absoluto < 1e9) return redondear(valor / 1e6) + " millones";
    if (absoluto < 1e12) return redondear(valor / 1e9) + " mil millones";
    if (absoluto < 1e15) return redondear(valor / 1e12) + " billones";
    return notacionCientifica(valor);
  }

  function formatearMilisegundos(ms) {
    return formatearTiempo(ms / 1000);
  }

  /**
   * Con 2ⁿ o n! se rebasa enseguida el número más grande que puede guardar el
   * ordenador, así que a partir de cierto punto se trabaja con el logaritmo del
   * valor en lugar del valor. «10^301 años» enseña más que «infinito».
   */
  function formatearTiempoLog10(log10Segundos) {
    if (log10Segundos < 290)
      return formatearTiempo(Math.pow(10, log10Segundos));
    const log10Anos = log10Segundos - Math.log10(SEGUNDOS_POR_ANO);
    return "10^" + Math.round(log10Anos) + " años";
  }

  function formatearCantidadLog10(log10Valor) {
    if (log10Valor < 15) return formatearCantidad(Math.pow(10, log10Valor));
    const exponente = Math.floor(log10Valor);
    const mantisa = Math.pow(10, log10Valor - exponente);
    return redondear(mantisa, 1) + "·10^" + exponente;
  }

  /** log₁₀(n!) sumando logaritmos: no desborda nunca. */
  function log10Factorial(n) {
    let total = 0;
    for (let i = 2; i <= n; i++) total += Math.log10(i);
    return total;
  }

  function cederControl() {
    return new Promise(function (resolver) {
      setTimeout(resolver, 0);
    });
  }

  function siguienteCuadro() {
    return new Promise(function (resolver) {
      requestAnimationFrame(function () {
        resolver();
      });
    });
  }

  function limitar(valor, minimo, maximo) {
    return Math.min(maximo, Math.max(minimo, valor));
  }

  function interpolar(desde, hasta, avance) {
    return desde + (hasta - desde) * avance;
  }

  /** Suavizado para que las animaciones no arranquen ni frenen de golpe. */
  function suavizar(t) {
    return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  }

  function elemento(selector, raiz) {
    return (raiz || document).querySelector(selector);
  }

  function elementos(selector, raiz) {
    return Array.prototype.slice.call(
      (raiz || document).querySelectorAll(selector),
    );
  }

  function crear(etiqueta, clases, texto) {
    const nodo = document.createElement(etiqueta);
    if (clases) nodo.className = clases;
    if (texto != null) nodo.textContent = texto;
    return nodo;
  }

  /**
   * Prepara un canvas para pantallas de alta densidad y devuelve el contexto
   * con las dimensiones lógicas ya calculadas.
   */
  function prepararLienzo(canvas) {
    const densidad = Math.min(global.devicePixelRatio || 1, 2);
    const ancho = canvas.clientWidth || canvas.parentElement.clientWidth || 800;
    const alto = canvas.clientHeight || 320;
    canvas.width = Math.round(ancho * densidad);
    canvas.height = Math.round(alto * densidad);
    const contexto = canvas.getContext("2d");
    contexto.setTransform(densidad, 0, 0, densidad, 0, 0);
    return { contexto: contexto, ancho: ancho, alto: alto };
  }

  TP.utiles = {
    SEGUNDOS_POR_ANO: SEGUNDOS_POR_ANO,
    EDAD_UNIVERSO_ANOS: EDAD_UNIVERSO_ANOS,
    redondear: redondear,
    formatearTiempo: formatearTiempo,
    formatearTiempoLog10: formatearTiempoLog10,
    formatearMilisegundos: formatearMilisegundos,
    formatearCantidad: formatearCantidad,
    formatearCantidadLog10: formatearCantidadLog10,
    log10Factorial: log10Factorial,
    notacionCientifica: notacionCientifica,
    cederControl: cederControl,
    siguienteCuadro: siguienteCuadro,
    limitar: limitar,
    interpolar: interpolar,
    suavizar: suavizar,
    elemento: elemento,
    elementos: elementos,
    crear: crear,
    prepararLienzo: prepararLienzo,
  };
})(window);
