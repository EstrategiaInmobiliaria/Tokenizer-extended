/**
 * Montaje de la aplicación: conecta los controles con el motor de medición, la
 * gráfica, la carrera, la extrapolación y el visor paso a paso.
 */
(function (global) {
  "use strict";

  const TP = global.TP;
  const utiles = TP.utiles;
  const $ = utiles.elemento;

  const estado = {
    opsPorSegundo: 1e9,
    velocidadMedida: null,
    midiendo: false,
    cancelar: false,
    series: [],
    aceleracionManual: false,
  };

  /* ------------------------------------------------------------------ chips */

  function crearChips(contenedor, algoritmos, idsActivos, alCambiar) {
    const activos = {};
    algoritmos.forEach(function (algoritmo) {
      activos[algoritmo.id] = idsActivos.indexOf(algoritmo.id) !== -1;
    });

    algoritmos.forEach(function (algoritmo) {
      const chip = utiles.crear("button", "chip");
      chip.type = "button";
      chip.style.color = algoritmo.color;
      const punto = utiles.crear("span", "punto-clase");
      punto.style.background = algoritmo.color;
      chip.appendChild(punto);
      chip.appendChild(document.createTextNode(algoritmo.clase));
      chip.title = algoritmo.nombre + " — " + algoritmo.resumen;
      chip.classList.toggle("activa", activos[algoritmo.id]);
      chip.addEventListener("click", function () {
        activos[algoritmo.id] = !activos[algoritmo.id];
        chip.classList.toggle("activa", activos[algoritmo.id]);
        if (alCambiar) alCambiar(seleccion());
      });
      contenedor.appendChild(chip);
    });

    function seleccion() {
      return algoritmos.filter(function (algoritmo) {
        return activos[algoritmo.id];
      });
    }

    return { seleccion: seleccion };
  }

  /* -------------------------------------------------- 1 · la idea clave */

  const TAMANOS_IDEA = [8, 16, 32, 64, 128, 256, 512, 1024];
  const filasIdea = new TP.FilasComplejidad($("#filas-idea"), TP.ALGORITMOS);
  const rangoIdea = $("#rango-n-idea");

  function pintarIdea() {
    const n = TAMANOS_IDEA[Number(rangoIdea.value)];
    $("#valor-n-idea").textContent = n.toLocaleString("es-ES");
    filasIdea.actualizar(function (algoritmo) {
      const log10Ahora = algoritmo.log10Operaciones(n);
      const log10Doble = algoritmo.log10Operaciones(2 * n);
      const log10Factor = log10Doble - log10Ahora;
      const textoFactor =
        log10Factor < 4
          ? "al duplicar n: ×" +
            utiles.redondear(
              Math.pow(10, log10Factor),
              Math.pow(10, log10Factor) < 10 ? 1 : 0,
            )
          : "al duplicar n: ×" + utiles.formatearCantidadLog10(log10Factor);
      return {
        log10Peso: log10Ahora,
        principal: utiles.formatearCantidadLog10(log10Ahora) + " operaciones",
        secundario: textoFactor,
        destacado: algoritmo.familia !== "polinomica",
      };
    });
  }

  rangoIdea.addEventListener("input", pintarIdea);
  $("#boton-duplicar").addEventListener("click", function () {
    const siguiente = Math.min(
      TAMANOS_IDEA.length - 1,
      Number(rangoIdea.value) + 1,
    );
    rangoIdea.value = String(siguiente);
    pintarIdea();
    if (siguiente === TAMANOS_IDEA.length - 1) {
      $("#aviso-idea").textContent =
        "Con n = 1024 los polinómicos siguen en cifras manejables. Las dos últimas filas ya han dejado de tener sentido físico: no hay ordenador ni tiempo para eso.";
    }
  });
  $("#boton-reset-idea").addEventListener("click", function () {
    rangoIdea.value = "3";
    pintarIdea();
    $("#aviso-idea").textContent =
      "Mueve el mando o pulsa «Duplicar n» y fíjate en el número de la derecha: es por cuánto se multiplica el trabajo cada vez que doblas la entrada.";
  });

  /* ------------------------------------------------- 2 · laboratorio */

  const grafica = new TP.Grafica($("#lienzo-grafica"));
  const chipsLaboratorio = crearChips(
    $("#chips-laboratorio"),
    TP.ALGORITMOS,
    ["logaritmica", "lineal", "nlogn", "cuadratica", "exponencial"],
    null,
  );
  const cuerpoTabla = $("#tabla-resultados tbody");
  const leyendaGrafica = $("#leyenda-grafica");

  $("#check-escala-log").addEventListener("change", function (evento) {
    grafica.configurar({
      escalaX: evento.target.checked ? "log" : "lineal",
      escalaY: evento.target.checked ? "log" : "lineal",
    });
  });
  $("#check-teorica").addEventListener("change", function (evento) {
    grafica.configurar({ mostrarTeorica: evento.target.checked });
  });

  function ponerEstado(texto, midiendo) {
    const nodo = $("#estado-medicion");
    nodo.textContent = texto;
    nodo.classList.toggle("midiendo", !!midiendo);
  }

  function ponerProgreso(fraccion) {
    $("#progreso").style.width = utiles.limitar(fraccion, 0, 1) * 100 + "%";
  }

  function anadirLeyenda(algoritmo) {
    const elemento = utiles.crear("span", "leyenda-elemento");
    const punto = utiles.crear("span", "punto-clase");
    punto.style.background = algoritmo.color;
    elemento.appendChild(punto);
    elemento.appendChild(
      document.createTextNode(algoritmo.clase + " · " + algoritmo.nombre),
    );
    leyendaGrafica.appendChild(elemento);
  }

  function anadirFilaTabla(algoritmo, punto, anterior) {
    const fila = utiles.crear("tr");
    fila.dataset.familia = algoritmo.familia;

    const celdaClase = utiles.crear("th");
    const marca = utiles.crear("span", "punto-clase");
    marca.style.background = algoritmo.color;
    celdaClase.appendChild(marca);
    celdaClase.appendChild(document.createTextNode(" " + algoritmo.clase));
    fila.appendChild(celdaClase);

    fila.appendChild(
      utiles.crear("td", "numero", punto.n.toLocaleString("es-ES")),
    );
    fila.appendChild(
      utiles.crear(
        "td",
        "numero",
        utiles.formatearMilisegundos(punto.msPorEjecucion),
      ),
    );

    if (anterior) {
      const factorN = punto.n / anterior.n;
      const factorTiempo = punto.msPorEjecucion / anterior.msPorEjecucion;
      fila.appendChild(
        utiles.crear("td", "numero", "×" + utiles.redondear(factorN, 1)),
      );
      const celdaTiempo = utiles.crear(
        "td",
        "numero destacar-celda",
        "×" +
          (factorTiempo > 1000
            ? utiles.formatearCantidad(factorTiempo)
            : utiles.redondear(factorTiempo, 2)),
      );
      fila.appendChild(celdaTiempo);
    } else {
      fila.appendChild(utiles.crear("td", "numero", "—"));
      fila.appendChild(utiles.crear("td", "numero", "—"));
    }

    fila.appendChild(
      utiles.crear("td", "numero", utiles.redondear(punto.nsPorOperacion, 2)),
    );
    cuerpoTabla.appendChild(fila);
  }

  function mediaGeometrica(valores) {
    if (!valores.length) return null;
    let suma = 0;
    valores.forEach(function (valor) {
      suma += Math.log(valor);
    });
    return Math.exp(suma / valores.length);
  }

  function escribirConclusiones(series) {
    const contenedor = $("#conclusiones");
    contenedor.innerHTML = "";

    series.forEach(function (serie) {
      if (serie.puntos.length < 2) return;
      const algoritmo = serie.algoritmo;
      const analisis = TP.medicion.estadisticas(serie);
      const factores = analisis.saltos.map(function (salto) {
        return salto.factorTiempo;
      });
      const factorMedio = mediaGeometrica(factores);

      const bloque = utiles.crear("div", "conclusion");
      bloque.style.color = algoritmo.color;
      const texto = utiles.crear("div", "conclusion-texto");

      let mensaje;
      if (algoritmo.familia === "polinomica") {
        const teorico = mediaGeometrica(
          analisis.saltos.map(function (salto) {
            return salto.factorTeorico;
          }),
        );
        mensaje =
          algoritmo.clase +
          " · " +
          algoritmo.nombre +
          ": al doblar n, el tiempo real se multiplicó por " +
          utiles.redondear(factorMedio, 2) +
          " (la teoría predice ×" +
          utiles.redondear(teorico, 2) +
          "). El exponente que sale de tus medidas es k ≈ " +
          utiles.redondear(analisis.exponenteEmpirico, 2) +
          ", así que el tiempo cabe dentro de c·n^k: es polinómico.";
      } else {
        mensaje =
          algoritmo.clase +
          " · " +
          algoritmo.nombre +
          ": cada " +
          algoritmo.cambioN.replace("+", "+") +
          " en n multiplicó el tiempo por " +
          utiles.redondear(factorMedio, 2) +
          ". El factor no depende de lo grande que sea n: siempre vuelve a doblarse. Eso no lo puede acotar ninguna potencia fija de n.";
        if (serie.muro) {
          mensaje +=
            " La serie se paró en n = " +
            serie.muro.n +
            " porque esa única medida habría tardado " +
            utiles.formatearMilisegundos(serie.muro.estimacionMs) +
            ".";
        }
      }

      texto.textContent = mensaje;
      bloque.appendChild(texto);
      contenedor.appendChild(bloque);
    });

    if (!contenedor.children.length) {
      contenedor.appendChild(
        utiles.crear(
          "p",
          "apagado",
          "No hubo suficientes medidas para sacar conclusiones. Prueba con un tiempo máximo por medida más largo.",
        ),
      );
    }
  }

  function elegirVelocidad(series) {
    const preferencia = [
      "lineal",
      "nlogn",
      "cuadratica",
      "cubica",
      "exponencial",
      "logaritmica",
      "factorial",
    ];
    for (let i = 0; i < preferencia.length; i++) {
      const encontrada = series.filter(function (serie) {
        return serie.algoritmo.id === preferencia[i] && serie.puntos.length;
      })[0];
      if (encontrada) {
        const analisis = TP.medicion.estadisticas(encontrada);
        if (analisis.operacionesPorSegundo) {
          return {
            opsPorSegundo: analisis.operacionesPorSegundo,
            origen: encontrada.algoritmo,
          };
        }
      }
    }
    return null;
  }

  function aplicarVelocidad(opsPorSegundo, origen) {
    estado.opsPorSegundo = opsPorSegundo;
    estado.velocidadMedida = opsPorSegundo;
    const nucleos = navigator.hardwareConcurrency
      ? navigator.hardwareConcurrency + " núcleos lógicos"
      : "núcleos desconocidos";
    $("#nota-maquina").textContent =
      "Velocidad medida en este ordenador: " +
      utiles.formatearCantidad(opsPorSegundo) +
      " operaciones por segundo (a partir de " +
      origen.clase +
      "). " +
      nucleos +
      ". Todas las estimaciones de las secciones 3, 4 y 5 usan esta cifra.";
    actualizarPared();
    actualizarCarrera(true);
    actualizarDuplicacion();
  }

  async function medir() {
    if (estado.midiendo) return;
    const seleccion = chipsLaboratorio.seleccion();
    if (!seleccion.length) {
      ponerEstado("Marca al menos una clase de complejidad para medir.");
      return;
    }

    estado.midiendo = true;
    estado.cancelar = false;
    estado.series = [];
    $("#boton-medir").disabled = true;
    $("#boton-cancelar").disabled = false;
    grafica.limpiar();
    cuerpoTabla.innerHTML = "";
    leyendaGrafica.innerHTML = "";
    $("#conclusiones").innerHTML = "";
    ponerProgreso(0);

    for (let indice = 0; indice < seleccion.length; indice++) {
      if (estado.cancelar) break;
      const algoritmo = seleccion[indice];
      anadirLeyenda(algoritmo);
      let anterior = null;

      const serie = await TP.medicion.medirSerie(algoritmo, {
        presupuestoMs: Number($("#select-presupuesto").value),
        cancelado: function () {
          return estado.cancelar;
        },
        alEmpezarPunto: function (n) {
          ponerEstado(
            "Midiendo " +
              algoritmo.clase +
              " · " +
              algoritmo.nombre +
              " con n = " +
              n.toLocaleString("es-ES") +
              "…",
            true,
          );
        },
        alPunto: function (punto) {
          grafica.anadirPunto(algoritmo, punto);
          anadirFilaTabla(algoritmo, punto, anterior);
          anterior = punto;
          const dentro =
            algoritmo.tamanos.indexOf(punto.n) / algoritmo.tamanos.length;
          ponerProgreso((indice + Math.max(0.1, dentro)) / seleccion.length);
        },
      });

      estado.series.push(serie);
      if (serie.muro) {
        ponerEstado(
          "Pared alcanzada en " +
            algoritmo.clase +
            ": medir n = " +
            serie.muro.n +
            " habría llevado " +
            utiles.formatearMilisegundos(serie.muro.estimacionMs) +
            ".",
          true,
        );
        await new Promise(function (resolver) {
          setTimeout(resolver, 900);
        });
      }
      ponerProgreso((indice + 1) / seleccion.length);
    }

    estado.midiendo = false;
    $("#boton-medir").disabled = false;
    $("#boton-cancelar").disabled = true;
    ponerEstado(
      estado.cancelar
        ? "Medición detenida. Los puntos ya medidos siguen en la gráfica."
        : "Medición terminada. Pasa el ratón por los puntos para ver los detalles.",
      false,
    );
    escribirConclusiones(estado.series);
    const velocidad = elegirVelocidad(estado.series);
    if (velocidad) aplicarVelocidad(velocidad.opsPorSegundo, velocidad.origen);
  }

  $("#boton-medir").addEventListener("click", medir);
  $("#boton-cancelar").addEventListener("click", function () {
    estado.cancelar = true;
    ponerEstado("Deteniendo…", true);
  });

  /* --------------------------------------------------- 3 · la carrera */

  const carrera = new TP.Carrera($("#lienzo-carrera"));
  const chipsCarrera = crearChips(
    $("#chips-carrera"),
    TP.ALGORITMOS,
    ["lineal", "nlogn", "cuadratica", "cubica", "exponencial"],
    function () {
      actualizarCarrera(true);
    },
  );
  const rangoCarrera = $("#rango-n-carrera");
  const rangoAceleracion = $("#rango-aceleracion");

  function velocidadElegida() {
    const valor = $("#select-velocidad").value;
    if (valor === "medida") return estado.velocidadMedida || 1e9;
    return Number(valor);
  }

  function actualizarCarrera(reiniciar) {
    const n = Number(rangoCarrera.value);
    $("#valor-n-carrera").textContent = String(n);
    carrera.configurar({
      algoritmos: chipsCarrera.seleccion(),
      n: n,
      opsPorSegundo: velocidadElegida(),
    });
    if (!estado.aceleracionManual) {
      const sugerida = carrera.aceleracionSugerida(12);
      rangoAceleracion.value = String(
        utiles.limitar(Math.log10(Math.max(sugerida, 1e-6)), -6, 24),
      );
    }
    carrera.aceleracion = Math.pow(10, Number(rangoAceleracion.value));
    if (reiniciar) carrera.reiniciar();
    pintarRelojes();
  }

  function pintarRelojes() {
    $("#reloj-simulado").textContent = utiles.formatearTiempo(
      carrera.tiempoSimulado,
    );
    $("#reloj-factor").textContent =
      utiles.formatearTiempo(carrera.aceleracion) + " de máquina";
    const velocidad = velocidadElegida();
    $("#reloj-velocidad").textContent =
      utiles.formatearCantidad(velocidad) +
      " op/s" +
      (estado.velocidadMedida && velocidad === estado.velocidadMedida
        ? " (medidas)"
        : "");
  }

  carrera.alActualizar = pintarRelojes;

  rangoCarrera.addEventListener("input", function () {
    actualizarCarrera(true);
  });
  rangoAceleracion.addEventListener("input", function () {
    estado.aceleracionManual = true;
    carrera.aceleracion = Math.pow(10, Number(rangoAceleracion.value));
    $("#valor-aceleracion").textContent = utiles.formatearTiempo(
      carrera.aceleracion,
    );
    pintarRelojes();
  });
  $("#select-velocidad").addEventListener("change", function () {
    actualizarCarrera(true);
  });
  $("#boton-auto-aceleracion").addEventListener("click", function () {
    estado.aceleracionManual = false;
    actualizarCarrera(false);
    $("#valor-aceleracion").textContent = "auto";
  });

  const botonCarrera = $("#boton-carrera");
  botonCarrera.addEventListener("click", function () {
    if (carrera.todosTerminados()) carrera.reiniciar();
    const corriendo = carrera.alternar();
    botonCarrera.textContent = corriendo ? "⏸ Pausa" : "▶ Salida";
  });
  $("#boton-reiniciar-carrera").addEventListener("click", function () {
    carrera.pausar();
    carrera.reiniciar();
    botonCarrera.textContent = "▶ Salida";
  });

  /* ----------------------------------------- 4 · la pared exponencial */

  const TAMANOS_PARED = [10, 20, 30, 40, 50, 64, 100, 1000, 1000000];
  const filasPared = new TP.FilasComplejidad($("#filas-pared"), TP.ALGORITMOS);
  const tablaLimites = new TP.TablaLimites($("#tabla-limites"), TP.ALGORITMOS);
  let nPared = 50;

  const chipsPared = $("#chips-pared");
  TAMANOS_PARED.forEach(function (n) {
    const chip = utiles.crear("button", "chip");
    chip.type = "button";
    chip.textContent = "n = " + utiles.formatearCantidad(n);
    chip.classList.toggle("activa", n === nPared);
    chip.addEventListener("click", function () {
      nPared = n;
      utiles.elementos(".chip", chipsPared).forEach(function (otro) {
        otro.classList.remove("activa");
      });
      chip.classList.add("activa");
      actualizarPared();
    });
    chipsPared.appendChild(chip);
  });

  function actualizarPared() {
    $("#valor-n-pared").textContent = nPared.toLocaleString("es-ES");
    const log10Velocidad = Math.log10(estado.opsPorSegundo);
    filasPared.actualizar(function (algoritmo) {
      const log10Operaciones = algoritmo.log10Operaciones(nPared);
      const log10Segundos = log10Operaciones - log10Velocidad;
      return {
        log10Peso: log10Segundos,
        principal: utiles.formatearTiempoLog10(log10Segundos),
        secundario:
          utiles.formatearCantidadLog10(log10Operaciones) + " operaciones",
        destacado: log10Segundos > Math.log10(utiles.SEGUNDOS_POR_ANO),
      };
    });
    tablaLimites.actualizar(estado.opsPorSegundo);
    $("#nota-pared").textContent =
      "Cálculo hecho con " +
      utiles.formatearCantidad(estado.opsPorSegundo) +
      " operaciones por segundo" +
      (estado.velocidadMedida
        ? " (medidas en tu ordenador en la sección 2)."
        : " (valor por defecto: mide en la sección 2 para usar el de tu ordenador).");
  }

  /* ------------------------------------------------- 5 · paso a paso */

  const visor = new TP.VisorPasoAPaso({
    lienzoLineal: $("#lienzo-lineal"),
    lienzoBurbuja: $("#lienzo-burbuja"),
  });
  const botonPasos = $("#boton-pasos");

  visor.alActualizar = function (visorActual) {
    $("#contador-lineal").textContent =
      visorActual.lineal.comparaciones.toLocaleString("es-ES");
    $("#contador-burbuja").textContent =
      visorActual.burbuja.comparaciones.toLocaleString("es-ES");
    $("#tiempo-lineal").textContent =
      utiles.redondear(visorActual.lineal.segundos, 1) + " s";
    $("#tiempo-burbuja").textContent =
      utiles.redondear(visorActual.burbuja.segundos, 1) + " s";
    $("#insignia-lineal").hidden = !visorActual.lineal.terminado;
    $("#insignia-burbuja").hidden = !visorActual.burbuja.terminado;
    if (!visorActual.corriendo) botonPasos.textContent = "▶ Arrancar los dos";

    const n = visorActual.n;
    const proporcion = (n - 1) / 2;
    $("#nota-pasos").textContent =
      "Con n = " +
      n +
      ", la búsqueda lineal necesita " +
      n +
      " comparaciones y la burbuja " +
      utiles.formatearCantidad((n * (n - 1)) / 2) +
      ": " +
      utiles.redondear(proporcion, 1) +
      " veces más trabajo. Si duplicas n esa proporción también se duplica, y por eso la distancia entre O(n) y O(n²) no deja de crecer.";
  };

  $("#rango-n-pasos").addEventListener("input", function (evento) {
    const n = Number(evento.target.value);
    $("#valor-n-pasos").textContent = String(n);
    visor.cambiarN(n);
    botonPasos.textContent = "▶ Arrancar los dos";
  });
  $("#rango-velocidad-pasos").addEventListener("input", function (evento) {
    visor.velocidad = Number(evento.target.value);
    $("#valor-velocidad-pasos").textContent = evento.target.value;
  });
  botonPasos.addEventListener("click", function () {
    const corriendo = visor.alternar();
    botonPasos.textContent = corriendo ? "⏸ Pausa" : "▶ Arrancar los dos";
  });
  $("#boton-reiniciar-pasos").addEventListener("click", function () {
    visor.pausar();
    visor.reiniciar();
    botonPasos.textContent = "▶ Arrancar los dos";
  });

  /* ------------------------------- 5b · duplicación exponencial */

  const duplicacion = new TP.DuplicacionExponencial($("#lienzo-duplicacion"));
  const rangoDuplicacion = $("#rango-n-duplicacion");

  function actualizarDuplicacion() {
    const n = Number(rangoDuplicacion.value);
    const combinaciones = Math.pow(2, n);
    $("#valor-n-duplicacion").textContent = String(n);
    $("#valor-combinaciones").textContent =
      utiles.formatearCantidad(combinaciones);
    $("#valor-tiempo-duplicacion").textContent = utiles.formatearTiempo(
      combinaciones / estado.opsPorSegundo,
    );
  }

  rangoDuplicacion.addEventListener("input", function () {
    duplicacion.cambiarN(Number(rangoDuplicacion.value));
    actualizarDuplicacion();
  });
  $("#boton-anadir-objeto").addEventListener("click", function () {
    const siguiente = Math.min(
      Number(rangoDuplicacion.max),
      Number(rangoDuplicacion.value) + 1,
    );
    rangoDuplicacion.value = String(siguiente);
    duplicacion.cambiarN(siguiente);
    actualizarDuplicacion();
  });

  /* ------------------------------------------ navegación e interfaz */

  const botonPresentacion = $("#boton-presentacion");
  botonPresentacion.addEventListener("click", function () {
    const activo = document.body.classList.toggle("presentacion");
    botonPresentacion.textContent = activo
      ? "Salir de presentación"
      : "Modo presentación";
    grafica.solicitarDibujo();
    carrera.pintar();
    visor.pintar();
    duplicacion.pintar();
  });

  $("#boton-tour").addEventListener("click", function () {
    document.getElementById("idea").scrollIntoView({ behavior: "smooth" });
  });

  const enlaces = utiles.elementos(".pastilla");
  if ("IntersectionObserver" in global) {
    const observador = new IntersectionObserver(
      function (entradas) {
        entradas.forEach(function (entrada) {
          if (!entrada.isIntersecting) return;
          enlaces.forEach(function (enlace) {
            enlace.classList.toggle(
              "activa",
              enlace.getAttribute("href") === "#" + entrada.target.id,
            );
          });
        });
      },
      { rootMargin: "-45% 0px -50% 0px" },
    );
    utiles.elementos(".seccion").forEach(function (seccion) {
      observador.observe(seccion);
    });
  }

  const SECCIONES = [
    "idea",
    "laboratorio",
    "carrera",
    "pared",
    "pasoapaso",
    "clase",
  ];
  document.addEventListener("keydown", function (evento) {
    const etiqueta = (evento.target.tagName || "").toLowerCase();
    if (
      etiqueta === "input" ||
      etiqueta === "select" ||
      etiqueta === "textarea"
    ) {
      return;
    }
    if (evento.key >= "1" && evento.key <= "6") {
      const destino = document.getElementById(
        SECCIONES[Number(evento.key) - 1],
      );
      if (destino) destino.scrollIntoView({ behavior: "smooth" });
      return;
    }
    if (evento.key === "p" || evento.key === "P") {
      botonPresentacion.click();
      return;
    }
    if (evento.key === "m" || evento.key === "M") {
      medir();
      return;
    }
    if (evento.key === " ") {
      evento.preventDefault();
      botonCarrera.click();
    }
  });

  global.addEventListener("resize", function () {
    grafica.solicitarDibujo();
    carrera.pintar();
    visor.pintar();
  });

  /* ------------------------------------------------ arranque inicial */

  pintarIdea();
  actualizarPared();
  actualizarCarrera(true);
  actualizarDuplicacion();
  $("#valor-aceleracion").textContent = "auto";
  visor.notificar();
  visor.pintar();
})(window);
