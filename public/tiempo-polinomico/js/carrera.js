/**
 * Carrera de algoritmos a escala real.
 *
 * Todos los carriles resuelven el MISMO problema de tamaño n. La velocidad de la
 * máquina (operaciones por segundo) sale de las mediciones reales del laboratorio,
 * así que el tiempo que ves correr en el reloj es tiempo de verdad, solo acelerado
 * o ralentizado por un factor que se muestra siempre en pantalla.
 */
(function (global) {
  "use strict";

  const TP = (global.TP = global.TP || {});
  const utiles = TP.utiles;

  const ALTO_CARRIL = 62;

  function Carrera(canvas) {
    this.canvas = canvas;
    this.carriles = [];
    this.n = 32;
    this.opsPorSegundo = 1e9;
    this.aceleracion = 1;
    this.tiempoSimulado = 0;
    this.corriendo = false;
    this.ultimoCuadro = 0;
    this.alActualizar = null;
    this.bucleActivo = false;
  }

  Carrera.prototype.configurar = function (opciones) {
    if (opciones.algoritmos) {
      const self = this;
      this.carriles = opciones.algoritmos.map(function (algoritmo) {
        return {
          algoritmo: algoritmo,
          operaciones: algoritmo.operaciones(self.n),
          progreso: 0,
          terminadoEn: null,
        };
      });
    }
    if (opciones.n != null) this.n = opciones.n;
    if (opciones.opsPorSegundo != null) {
      this.opsPorSegundo = opciones.opsPorSegundo;
    }
    if (opciones.aceleracion != null) this.aceleracion = opciones.aceleracion;
    this.recalcular();
    this.pintar();
  };

  Carrera.prototype.recalcular = function () {
    const self = this;
    this.carriles.forEach(function (carril) {
      carril.operaciones = carril.algoritmo.operaciones(self.n);
      carril.duracion = carril.operaciones / self.opsPorSegundo;
    });
  };

  /** Duración simulada del carril polinómico más lento (referencia de la animación). */
  Carrera.prototype.duracionReferencia = function () {
    let referencia = 0;
    this.carriles.forEach(function (carril) {
      if (carril.algoritmo.familia !== "polinomica") return;
      referencia = Math.max(referencia, carril.duracion);
    });
    if (referencia === 0) {
      this.carriles.forEach(function (carril) {
        referencia = Math.max(referencia, carril.duracion);
      });
    }
    return referencia;
  };

  /** Elige la aceleración para que la carrera dure unos `segundos` de clase. */
  Carrera.prototype.aceleracionSugerida = function (segundos) {
    const referencia = this.duracionReferencia();
    if (!referencia) return 1;
    return referencia / (segundos || 10);
  };

  Carrera.prototype.reiniciar = function () {
    this.tiempoSimulado = 0;
    this.carriles.forEach(function (carril) {
      carril.progreso = 0;
      carril.terminadoEn = null;
    });
    this.pintar();
    this.notificar();
  };

  Carrera.prototype.iniciar = function () {
    if (this.corriendo) return;
    this.corriendo = true;
    this.ultimoCuadro = performance.now();
    this.arrancarBucle();
  };

  Carrera.prototype.pausar = function () {
    this.corriendo = false;
  };

  Carrera.prototype.alternar = function () {
    if (this.corriendo) this.pausar();
    else this.iniciar();
    return this.corriendo;
  };

  Carrera.prototype.arrancarBucle = function () {
    if (this.bucleActivo) return;
    this.bucleActivo = true;
    const self = this;
    requestAnimationFrame(function paso(ahora) {
      const transcurridoReal = Math.min(ahora - self.ultimoCuadro, 100) / 1000;
      self.ultimoCuadro = ahora;
      if (self.corriendo) {
        self.tiempoSimulado += transcurridoReal * self.aceleracion;
        self.carriles.forEach(function (carril) {
          const avance = carril.duracion
            ? self.tiempoSimulado / carril.duracion
            : 1;
          carril.progreso = Math.min(1, avance);
          if (carril.progreso >= 1 && carril.terminadoEn == null) {
            carril.terminadoEn = carril.duracion;
          }
        });
        self.notificar();
      }
      self.pintar();
      if (self.corriendo) {
        requestAnimationFrame(paso);
      } else {
        self.bucleActivo = false;
      }
    });
  };

  Carrera.prototype.notificar = function () {
    if (this.alActualizar) this.alActualizar(this);
  };

  Carrera.prototype.todosTerminados = function () {
    return this.carriles.every(function (carril) {
      return carril.progreso >= 1;
    });
  };

  function textoRestante(carril, tiempoSimulado) {
    if (carril.progreso >= 1) {
      return "meta en " + utiles.formatearTiempo(carril.duracion);
    }
    const restante = Math.max(0, carril.duracion - tiempoSimulado);
    return "le faltan " + utiles.formatearTiempo(restante);
  }

  function porcentaje(progreso) {
    const valor = progreso * 100;
    if (valor >= 1) return utiles.redondear(valor, 1) + " %";
    if (valor >= 0.0001) return valor.toFixed(4) + " %";
    if (valor === 0) return "0 %";
    return utiles.notacionCientifica(valor) + " %";
  }

  Carrera.prototype.pintar = function () {
    const canvas = this.canvas;
    const altoDeseado = Math.max(1, this.carriles.length) * ALTO_CARRIL + 8;
    if (canvas.style.height !== altoDeseado + "px") {
      canvas.style.height = altoDeseado + "px";
    }
    const lienzo = utiles.prepararLienzo(canvas);
    const ctx = lienzo.contexto;
    const ancho = lienzo.ancho;
    ctx.clearRect(0, 0, ancho, lienzo.alto);

    const izquierda = 168;
    const derecha = ancho - 215;
    const ahora = performance.now();
    const self = this;

    this.carriles.forEach(function (carril, indice) {
      const y = indice * ALTO_CARRIL + 30;
      const color = carril.algoritmo.color;

      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.font = "bold 15px ui-monospace, SFMono-Regular, monospace";
      ctx.fillStyle = color;
      ctx.fillText(carril.algoritmo.clase, 8, y - 7);
      ctx.font = "11px ui-sans-serif, system-ui, sans-serif";
      ctx.fillStyle = "rgba(203, 213, 225, 0.7)";
      ctx.fillText(carril.algoritmo.nombre, 8, y + 10);

      // Pista
      ctx.strokeStyle = "rgba(148, 163, 184, 0.22)";
      ctx.lineWidth = 10;
      ctx.lineCap = "round";
      ctx.beginPath();
      ctx.moveTo(izquierda, y);
      ctx.lineTo(derecha, y);
      ctx.stroke();

      // Recorrido hecho
      const x = utiles.interpolar(izquierda, derecha, carril.progreso);
      ctx.strokeStyle = color;
      ctx.globalAlpha = 0.85;
      ctx.beginPath();
      ctx.moveTo(izquierda, y);
      ctx.lineTo(Math.max(izquierda, x), y);
      ctx.stroke();
      ctx.globalAlpha = 1;

      // Línea de meta
      ctx.strokeStyle = "rgba(226, 232, 240, 0.35)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(derecha, y - 14);
      ctx.lineTo(derecha, y + 14);
      ctx.stroke();

      // Corredor
      const pulso =
        carril.progreso >= 1
          ? 0
          : 2 * Math.sin((ahora / 220 + indice) % (Math.PI * 2));
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, 9 + pulso * 0.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
      ctx.beginPath();
      ctx.arc(x, y, 3.5, 0, Math.PI * 2);
      ctx.fill();

      if (carril.progreso >= 1) {
        ctx.fillStyle = color;
        ctx.font = "15px ui-sans-serif, system-ui, sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("🏁", derecha + 14, y);
      }

      ctx.textAlign = "left";
      ctx.font = "12px ui-monospace, SFMono-Regular, monospace";
      ctx.fillStyle =
        carril.progreso >= 1 ? color : "rgba(226, 232, 240, 0.85)";
      ctx.fillText(porcentaje(carril.progreso), derecha + 30, y - 7);
      ctx.font = "11px ui-sans-serif, system-ui, sans-serif";
      ctx.fillStyle = "rgba(148, 163, 184, 0.85)";
      ctx.fillText(
        textoRestante(carril, self.tiempoSimulado),
        derecha + 30,
        y + 10,
      );
    });
  };

  TP.Carrera = Carrera;
})(window);
