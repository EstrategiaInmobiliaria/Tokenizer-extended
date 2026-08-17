/**
 * Visor paso a paso: dos algoritmos reales trabajando sobre la MISMA lista, a la
 * misma velocidad de comparaciones por segundo, para que se vea con los ojos por
 * qué uno necesita n pasos y el otro n²/2.
 *
 * Además incluye la demostración de la duplicación exponencial: cada objeto nuevo
 * dobla el número de combinaciones que hay que probar.
 */
(function (global) {
  "use strict";

  const TP = (global.TP = global.TP || {});
  const utiles = TP.utiles;

  function listaDesordenada(n) {
    const valores = [];
    for (let i = 0; i < n; i++) valores.push((i + 1) / n);
    // Mezcla determinista para que la clase repita el mismo ejemplo.
    let semilla = 20240607;
    for (let i = n - 1; i > 0; i--) {
      semilla = (semilla * 1103515245 + 12345) & 0x7fffffff;
      const j = semilla % (i + 1);
      const temporal = valores[i];
      valores[i] = valores[j];
      valores[j] = temporal;
    }
    return valores;
  }

  function* pasosBusquedaLineal(estado) {
    const objetivo = estado.objetivo;
    for (let i = 0; i < estado.valores.length; i++) {
      estado.foco = [i];
      estado.comparaciones += 1;
      yield;
      if (estado.valores[i] === objetivo) {
        estado.encontrado = i;
        estado.foco = [i];
        return;
      }
    }
    estado.foco = [];
  }

  function* pasosBurbuja(estado) {
    const valores = estado.valores;
    const n = valores.length;
    for (let i = 0; i < n - 1; i++) {
      for (let j = 0; j < n - 1 - i; j++) {
        estado.foco = [j, j + 1];
        estado.comparaciones += 1;
        yield;
        if (valores[j] > valores[j + 1]) {
          const temporal = valores[j];
          valores[j] = valores[j + 1];
          valores[j + 1] = temporal;
          estado.intercambios += 1;
        }
      }
      estado.ordenadosDesde = n - 1 - i;
    }
    estado.ordenadosDesde = 0;
    estado.foco = [];
  }

  function dibujarLista(canvas, estado, color) {
    const lienzo = utiles.prepararLienzo(canvas);
    const ctx = lienzo.contexto;
    const ancho = lienzo.ancho;
    const alto = lienzo.alto;
    ctx.clearRect(0, 0, ancho, alto);

    const n = estado.valores.length;
    const separacion = n > 60 ? 1 : 2;
    const anchoBarra = Math.max(2, ancho / n - separacion);
    const base = alto - 4;
    const altoMaximo = alto - 14;

    for (let i = 0; i < n; i++) {
      const x = (ancho / n) * i;
      const altura = Math.max(3, estado.valores[i] * altoMaximo);
      const enFoco = estado.foco.indexOf(i) !== -1;
      const yaOrdenado =
        estado.ordenadosDesde != null && i >= estado.ordenadosDesde;
      if (enFoco) ctx.fillStyle = color;
      else if (yaOrdenado) ctx.fillStyle = "rgba(74, 222, 128, 0.45)";
      else ctx.fillStyle = "rgba(148, 163, 184, 0.4)";
      ctx.fillRect(x, base - altura, anchoBarra, altura);
    }

    if (estado.encontrado != null) {
      const x = (ancho / n) * estado.encontrado;
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.strokeRect(x - 1, 4, anchoBarra + 2, alto - 8);
    }
  }

  /**
   * Controla los dos paneles animados. `comparacionesPorSegundo` es el mismo para
   * los dos, así que la diferencia de tiempo es únicamente la del algoritmo.
   */
  function VisorPasoAPaso(referencias) {
    this.referencias = referencias;
    this.n = 28;
    this.velocidad = 40;
    this.corriendo = false;
    this.bucleActivo = false;
    this.resto = 0;
    this.alActualizar = null;
    this.reiniciar();
  }

  VisorPasoAPaso.prototype.reiniciar = function () {
    const base = listaDesordenada(this.n);
    const objetivo = base[base.length - 1];

    this.lineal = {
      valores: base.slice(),
      objetivo: objetivo,
      foco: [],
      comparaciones: 0,
      intercambios: 0,
      encontrado: null,
      ordenadosDesde: null,
      terminado: false,
      segundos: 0,
    };
    this.burbuja = {
      valores: base.slice(),
      objetivo: objetivo,
      foco: [],
      comparaciones: 0,
      intercambios: 0,
      encontrado: null,
      ordenadosDesde: null,
      terminado: false,
      segundos: 0,
    };
    this.iteradorLineal = pasosBusquedaLineal(this.lineal);
    this.iteradorBurbuja = pasosBurbuja(this.burbuja);
    this.transcurrido = 0;
    this.resto = 0;
    this.pintar();
    this.notificar();
  };

  VisorPasoAPaso.prototype.cambiarN = function (n) {
    this.n = n;
    this.corriendo = false;
    this.reiniciar();
  };

  VisorPasoAPaso.prototype.iniciar = function () {
    if (this.corriendo) return;
    if (this.lineal.terminado && this.burbuja.terminado) this.reiniciar();
    this.corriendo = true;
    this.ultimoCuadro = performance.now();
    this.arrancarBucle();
  };

  VisorPasoAPaso.prototype.pausar = function () {
    this.corriendo = false;
  };

  VisorPasoAPaso.prototype.alternar = function () {
    if (this.corriendo) this.pausar();
    else this.iniciar();
    return this.corriendo;
  };

  VisorPasoAPaso.prototype.avanzar = function (pasos) {
    for (let i = 0; i < pasos; i++) {
      if (!this.lineal.terminado && this.iteradorLineal.next().done) {
        this.lineal.terminado = true;
      }
      if (!this.burbuja.terminado && this.iteradorBurbuja.next().done) {
        this.burbuja.terminado = true;
      }
      if (this.lineal.terminado && this.burbuja.terminado) return;
    }
  };

  VisorPasoAPaso.prototype.arrancarBucle = function () {
    if (this.bucleActivo) return;
    this.bucleActivo = true;
    const self = this;
    requestAnimationFrame(function paso(ahora) {
      const transcurrido = Math.min(ahora - self.ultimoCuadro, 100) / 1000;
      self.ultimoCuadro = ahora;
      if (self.corriendo) {
        self.transcurrido += transcurrido;
        if (!self.lineal.terminado) self.lineal.segundos = self.transcurrido;
        if (!self.burbuja.terminado) self.burbuja.segundos = self.transcurrido;
        self.resto += transcurrido * self.velocidad;
        const pasos = Math.floor(self.resto);
        self.resto -= pasos;
        if (pasos > 0) self.avanzar(pasos);
        self.notificar();
        if (self.lineal.terminado && self.burbuja.terminado) {
          self.corriendo = false;
        }
      }
      self.pintar();
      if (self.corriendo) {
        requestAnimationFrame(paso);
      } else {
        self.bucleActivo = false;
        self.notificar();
      }
    });
  };

  VisorPasoAPaso.prototype.pintar = function () {
    dibujarLista(this.referencias.lienzoLineal, this.lineal, "#4ade80");
    dibujarLista(this.referencias.lienzoBurbuja, this.burbuja, "#fbbf24");
  };

  VisorPasoAPaso.prototype.notificar = function () {
    if (this.alActualizar) this.alActualizar(this);
  };

  /**
   * Cada objeto que añades DUPLICA las combinaciones. Se dibuja una celda por
   * combinación, con una animación de aparición para que el salto se sienta.
   */
  function DuplicacionExponencial(canvas) {
    this.canvas = canvas;
    this.n = 4;
    this.nacimiento = performance.now();
    this.bucleActivo = false;
    this.pintar();
    const self = this;
    global.addEventListener("resize", function () {
      self.pintar();
    });
  }

  DuplicacionExponencial.prototype.cambiarN = function (n) {
    this.anterior = this.n;
    this.n = n;
    this.nacimiento = performance.now();
    this.animar();
  };

  DuplicacionExponencial.prototype.animar = function () {
    if (this.bucleActivo) return;
    this.bucleActivo = true;
    const self = this;
    requestAnimationFrame(function paso() {
      const continuar = self.pintar();
      if (continuar) requestAnimationFrame(paso);
      else self.bucleActivo = false;
    });
  };

  DuplicacionExponencial.prototype.pintar = function () {
    const lienzo = utiles.prepararLienzo(this.canvas);
    const ctx = lienzo.contexto;
    const ancho = lienzo.ancho;
    const alto = lienzo.alto;
    ctx.clearRect(0, 0, ancho, alto);

    const total = Math.pow(2, this.n);
    const columnas = Math.ceil(Math.sqrt((total * ancho) / alto)) || 1;
    const filas = Math.ceil(total / columnas);
    const lado = Math.max(1, Math.min(ancho / columnas, alto / filas) - 1);
    const anteriores = this.anterior != null ? Math.pow(2, this.anterior) : 0;
    const avance = utiles.limitar(
      (performance.now() - this.nacimiento) / 600,
      0,
      1,
    );

    for (let indice = 0; indice < total; indice++) {
      const columna = indice % columnas;
      const fila = Math.floor(indice / columnas);
      const x = columna * (lado + 1);
      const y = fila * (lado + 1);
      const esNuevo = indice >= anteriores;
      ctx.globalAlpha = esNuevo ? 0.15 + 0.85 * utiles.suavizar(avance) : 1;
      ctx.fillStyle = esNuevo ? "#f43f5e" : "rgba(244, 63, 94, 0.45)";
      const escala = esNuevo ? utiles.interpolar(0.3, 1, avance) : 1;
      const desplazamiento = (lado * (1 - escala)) / 2;
      ctx.fillRect(
        x + desplazamiento,
        y + desplazamiento,
        lado * escala,
        lado * escala,
      );
    }
    ctx.globalAlpha = 1;
    return avance < 1;
  };

  TP.VisorPasoAPaso = VisorPasoAPaso;
  TP.DuplicacionExponencial = DuplicacionExponencial;
})(window);
