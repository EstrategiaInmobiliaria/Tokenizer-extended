/**
 * Gráfica de dispersión animada sobre canvas.
 *
 * Dibuja los tiempos medidos de verdad (puntos + línea que se va trazando) y,
 * encima, la curva teórica c·f(n) ajustada al último punto de cada serie: cuando
 * las dos coinciden, el modelo de complejidad queda demostrado ante la clase.
 */
(function (global) {
  "use strict";

  const TP = (global.TP = global.TP || {});
  const utiles = TP.utiles;

  const DURACION_APARICION = 550;

  function Grafica(canvas) {
    this.canvas = canvas;
    this.series = [];
    this.escalaX = "log";
    this.escalaY = "log";
    this.mostrarTeorica = true;
    this.raton = null;
    this.animando = false;
    this.margen = { arriba: 18, derecha: 18, abajo: 44, izquierda: 74 };

    const self = this;
    canvas.addEventListener("mousemove", function (evento) {
      const caja = canvas.getBoundingClientRect();
      self.raton = {
        x: evento.clientX - caja.left,
        y: evento.clientY - caja.top,
      };
      self.solicitarDibujo();
    });
    canvas.addEventListener("mouseleave", function () {
      self.raton = null;
      self.solicitarDibujo();
    });
    global.addEventListener("resize", function () {
      self.solicitarDibujo();
    });
  }

  Grafica.prototype.limpiar = function () {
    this.series = [];
    this.solicitarDibujo();
  };

  Grafica.prototype.serie = function (algoritmo) {
    let encontrada = null;
    this.series.forEach(function (serie) {
      if (serie.algoritmo.id === algoritmo.id) encontrada = serie;
    });
    if (!encontrada) {
      encontrada = { algoritmo: algoritmo, puntos: [] };
      this.series.push(encontrada);
    }
    return encontrada;
  };

  Grafica.prototype.anadirPunto = function (algoritmo, punto) {
    const serie = this.serie(algoritmo);
    serie.puntos.push(Object.assign({ nacimiento: performance.now() }, punto));
    this.solicitarDibujo();
  };

  Grafica.prototype.configurar = function (opciones) {
    Object.assign(this, opciones);
    this.solicitarDibujo();
  };

  Grafica.prototype.solicitarDibujo = function () {
    if (this.animando) return;
    this.animando = true;
    const self = this;
    requestAnimationFrame(function paso() {
      const sigueAnimando = self.dibujar();
      if (sigueAnimando) {
        requestAnimationFrame(paso);
      } else {
        self.animando = false;
      }
    });
  };

  Grafica.prototype.limites = function () {
    let minX = Infinity;
    let maxX = -Infinity;
    let minY = Infinity;
    let maxY = -Infinity;
    this.series.forEach(function (serie) {
      serie.puntos.forEach(function (punto) {
        minX = Math.min(minX, punto.n);
        maxX = Math.max(maxX, punto.n);
        minY = Math.min(minY, punto.msPorEjecucion);
        maxY = Math.max(maxY, punto.msPorEjecucion);
      });
    });
    if (!isFinite(minX)) return null;
    if (maxX === minX) maxX = minX * 2;
    if (maxY === minY) maxY = minY * 2 + 0.001;
    if (this.escalaY === "lineal") minY = 0;
    else {
      minY = minY / 2;
      maxY = maxY * 2;
    }
    return { minX: minX, maxX: maxX, minY: minY, maxY: maxY };
  };

  function proyectar(valor, minimo, maximo, escala, desde, hasta) {
    let avance;
    if (escala === "log") {
      const seguro = Math.max(valor, minimo > 0 ? minimo : 1e-9);
      avance =
        (Math.log(seguro) - Math.log(minimo)) /
        (Math.log(maximo) - Math.log(minimo));
    } else {
      avance = (valor - minimo) / (maximo - minimo);
    }
    return utiles.interpolar(desde, hasta, utiles.limitar(avance, -0.2, 1.2));
  }

  function marcasLogaritmicas(minimo, maximo) {
    const marcas = [];
    let exponente = Math.floor(Math.log10(minimo));
    const limite = Math.ceil(Math.log10(maximo));
    while (exponente <= limite) {
      const valor = Math.pow(10, exponente);
      if (valor >= minimo * 0.99 && valor <= maximo * 1.01) marcas.push(valor);
      exponente += 1;
    }
    if (marcas.length < 3) {
      // Rango estrecho: añade los intermedios ×2 y ×5 para no dejar el eje vacío.
      const extra = [];
      marcas.forEach(function (valor) {
        [2, 5].forEach(function (factor) {
          const candidato = valor * factor;
          if (candidato >= minimo && candidato <= maximo) extra.push(candidato);
        });
      });
      return marcas.concat(extra).sort(function (a, b) {
        return a - b;
      });
    }
    return marcas;
  }

  function rectanguloRedondeado(ctx, x, y, ancho, alto, radio) {
    if (typeof ctx.roundRect === "function") {
      ctx.beginPath();
      ctx.roundRect(x, y, ancho, alto, radio);
      return;
    }
    ctx.beginPath();
    ctx.moveTo(x + radio, y);
    ctx.arcTo(x + ancho, y, x + ancho, y + alto, radio);
    ctx.arcTo(x + ancho, y + alto, x, y + alto, radio);
    ctx.arcTo(x, y + alto, x, y, radio);
    ctx.arcTo(x, y, x + ancho, y, radio);
    ctx.closePath();
  }

  function marcasLineales(minimo, maximo) {
    const marcas = [];
    const paso = (maximo - minimo) / 5;
    for (let i = 0; i <= 5; i++) marcas.push(minimo + paso * i);
    return marcas;
  }

  Grafica.prototype.dibujar = function () {
    const lienzo = utiles.prepararLienzo(this.canvas);
    const ctx = lienzo.contexto;
    const ancho = lienzo.ancho;
    const alto = lienzo.alto;
    const margen = this.margen;
    const izquierda = margen.izquierda;
    const derecha = ancho - margen.derecha;
    const arriba = margen.arriba;
    const abajo = alto - margen.abajo;

    ctx.clearRect(0, 0, ancho, alto);

    const limites = this.limites();
    if (!limites) {
      ctx.fillStyle = "rgba(226, 232, 240, 0.55)";
      ctx.font = "15px ui-sans-serif, system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(
        "Pulsa «Medir en mi ordenador» para llenar esta gráfica con tiempos reales",
        ancho / 2,
        alto / 2,
      );
      return false;
    }

    const self = this;
    const x = function (n) {
      return proyectar(
        n,
        limites.minX,
        limites.maxX,
        self.escalaX,
        izquierda,
        derecha,
      );
    };
    const y = function (ms) {
      return proyectar(
        ms,
        limites.minY,
        limites.maxY,
        self.escalaY,
        abajo,
        arriba,
      );
    };

    // Rejilla y ejes
    const marcasY =
      this.escalaY === "log"
        ? marcasLogaritmicas(limites.minY, limites.maxY)
        : marcasLineales(limites.minY, limites.maxY);
    ctx.font = "12px ui-monospace, SFMono-Regular, monospace";
    ctx.textBaseline = "middle";
    marcasY.forEach(function (valor) {
      const posicion = y(valor);
      ctx.strokeStyle = "rgba(148, 163, 184, 0.16)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(izquierda, posicion);
      ctx.lineTo(derecha, posicion);
      ctx.stroke();
      ctx.fillStyle = "rgba(203, 213, 225, 0.75)";
      ctx.textAlign = "right";
      ctx.fillText(
        utiles.formatearMilisegundos(valor),
        izquierda - 10,
        posicion,
      );
    });

    const marcasX =
      this.escalaX === "log"
        ? marcasLogaritmicas(limites.minX, limites.maxX)
        : marcasLineales(limites.minX, limites.maxX);
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    marcasX.forEach(function (valor) {
      const posicion = x(valor);
      ctx.strokeStyle = "rgba(148, 163, 184, 0.1)";
      ctx.beginPath();
      ctx.moveTo(posicion, arriba);
      ctx.lineTo(posicion, abajo);
      ctx.stroke();
      ctx.fillStyle = "rgba(203, 213, 225, 0.75)";
      ctx.fillText(utiles.formatearCantidad(valor), posicion, abajo + 8);
    });

    ctx.strokeStyle = "rgba(148, 163, 184, 0.5)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(izquierda, arriba);
    ctx.lineTo(izquierda, abajo);
    ctx.lineTo(derecha, abajo);
    ctx.stroke();

    ctx.fillStyle = "rgba(226, 232, 240, 0.7)";
    ctx.font = "12px ui-sans-serif, system-ui, sans-serif";
    ctx.textAlign = "right";
    ctx.textBaseline = "bottom";
    ctx.fillText("tamaño de la entrada (n) →", derecha, abajo + 36);
    ctx.save();
    ctx.translate(16, arriba + 6);
    ctx.rotate(-Math.PI / 2);
    ctx.textAlign = "left";
    ctx.fillText("tiempo real medido ↑", -((abajo - arriba) / 2) - 60, 0);
    ctx.restore();

    const ahora = performance.now();
    let sigueAnimando = false;

    // Curvas teóricas c·f(n), ancladas al último punto medido de cada serie.
    if (this.mostrarTeorica) {
      this.series.forEach(function (serie) {
        if (serie.puntos.length < 2) return;
        const ultimo = serie.puntos[serie.puntos.length - 1];
        const constante =
          ultimo.msPorEjecucion / serie.algoritmo.operaciones(ultimo.n);
        ctx.strokeStyle = serie.algoritmo.color;
        ctx.globalAlpha = 0.35;
        ctx.setLineDash([5, 5]);
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        const pasos = 60;
        for (let i = 0; i <= pasos; i++) {
          const avance = i / pasos;
          const n =
            self.escalaX === "log"
              ? Math.exp(
                  utiles.interpolar(
                    Math.log(limites.minX),
                    Math.log(limites.maxX),
                    avance,
                  ),
                )
              : utiles.interpolar(limites.minX, limites.maxX, avance);
          const ms = constante * serie.algoritmo.operaciones(n);
          const px = x(n);
          const py = y(ms);
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.globalAlpha = 1;
      });
    }

    // Series medidas
    this.series.forEach(function (serie) {
      const visibles = [];
      serie.puntos.forEach(function (punto) {
        const edad = ahora - punto.nacimiento;
        const avance = utiles.limitar(edad / DURACION_APARICION, 0, 1);
        if (avance < 1) sigueAnimando = true;
        visibles.push({ punto: punto, avance: utiles.suavizar(avance) });
      });

      ctx.strokeStyle = serie.algoritmo.color;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      visibles.forEach(function (entrada, indice) {
        const px = x(entrada.punto.n);
        const py = y(entrada.punto.msPorEjecucion);
        if (indice === 0) {
          ctx.moveTo(px, py);
          return;
        }
        const previo = visibles[indice - 1];
        const pxPrevio = x(previo.punto.n);
        const pyPrevio = y(previo.punto.msPorEjecucion);
        ctx.lineTo(
          utiles.interpolar(pxPrevio, px, entrada.avance),
          utiles.interpolar(pyPrevio, py, entrada.avance),
        );
      });
      ctx.stroke();

      visibles.forEach(function (entrada) {
        const px = x(entrada.punto.n);
        const py = y(entrada.punto.msPorEjecucion);
        const radio = 3 + 3 * entrada.avance;
        ctx.fillStyle = serie.algoritmo.color;
        ctx.globalAlpha = 0.25 + 0.75 * entrada.avance;
        ctx.beginPath();
        ctx.arc(px, py, radio, 0, Math.PI * 2);
        ctx.fill();
        if (entrada.avance < 1) {
          ctx.globalAlpha = (1 - entrada.avance) * 0.5;
          ctx.beginPath();
          ctx.arc(px, py, radio + 16 * (1 - entrada.avance), 0, Math.PI * 2);
          ctx.strokeStyle = serie.algoritmo.color;
          ctx.lineWidth = 2;
          ctx.stroke();
        }
        ctx.globalAlpha = 1;
      });
    });

    // Etiqueta flotante del punto más cercano al ratón
    if (this.raton) {
      let mejor = null;
      this.series.forEach(function (serie) {
        serie.puntos.forEach(function (punto) {
          const px = x(punto.n);
          const py = y(punto.msPorEjecucion);
          const distancia = Math.hypot(px - self.raton.x, py - self.raton.y);
          if (distancia < 26 && (!mejor || distancia < mejor.distancia)) {
            mejor = {
              distancia: distancia,
              punto: punto,
              serie: serie,
              px: px,
              py: py,
            };
          }
        });
      });
      if (mejor) {
        const lineas = [
          mejor.serie.algoritmo.clase + " · " + mejor.serie.algoritmo.nombre,
          "n = " + mejor.punto.n.toLocaleString("es-ES"),
          "tiempo = " +
            utiles.formatearMilisegundos(mejor.punto.msPorEjecucion),
          "operaciones ≈ " + utiles.formatearCantidad(mejor.punto.operaciones),
        ];
        ctx.font = "12px ui-sans-serif, system-ui, sans-serif";
        let anchoCaja = 0;
        lineas.forEach(function (linea) {
          anchoCaja = Math.max(anchoCaja, ctx.measureText(linea).width);
        });
        anchoCaja += 20;
        const altoCaja = lineas.length * 17 + 14;
        let cajaX = Math.min(mejor.px + 14, derecha - anchoCaja);
        let cajaY = Math.max(arriba, mejor.py - altoCaja - 10);
        ctx.fillStyle = "rgba(15, 23, 42, 0.94)";
        ctx.strokeStyle = mejor.serie.algoritmo.color;
        ctx.lineWidth = 1.5;
        rectanguloRedondeado(ctx, cajaX, cajaY, anchoCaja, altoCaja, 8);
        ctx.fill();
        ctx.stroke();
        ctx.textAlign = "left";
        ctx.textBaseline = "top";
        lineas.forEach(function (linea, indice) {
          ctx.fillStyle =
            indice === 0
              ? mejor.serie.algoritmo.color
              : "rgba(226,232,240,0.9)";
          ctx.fillText(linea, cajaX + 10, cajaY + 8 + indice * 17);
        });
      }
    }

    return sigueAnimando;
  };

  TP.Grafica = Grafica;
})(window);
