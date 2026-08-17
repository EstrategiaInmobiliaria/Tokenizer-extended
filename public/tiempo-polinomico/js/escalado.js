/**
 * Escalado: qué pasa cuando n crece de verdad.
 *
 * Con la velocidad real medida en el laboratorio (operaciones por segundo de ESTE
 * ordenador) se extrapola el tiempo que tardaría cada clase de complejidad y se
 * traduce a unidades que la clase pueda imaginar: segundos, días, años, universos.
 */
(function (global) {
  "use strict";

  const TP = (global.TP = global.TP || {});
  const utiles = TP.utiles;

  /** Filas con barra logarítmica reutilizables (idea clave y pared exponencial). */
  function FilasComplejidad(contenedor, algoritmos) {
    this.contenedor = contenedor;
    this.filas = algoritmos.map(function (algoritmo) {
      const fila = utiles.crear("div", "fila-complejidad");
      fila.dataset.familia = algoritmo.familia;

      const clase = utiles.crear("div", "fc-clase", algoritmo.clase);
      clase.style.color = algoritmo.color;

      const cuerpo = utiles.crear("div", "fc-cuerpo");
      const pista = utiles.crear("div", "fc-barra");
      const relleno = utiles.crear("span", "fc-relleno");
      relleno.style.background = algoritmo.color;
      pista.appendChild(relleno);

      const datos = utiles.crear("div", "fc-datos");
      const principal = utiles.crear("span", "fc-principal");
      const secundario = utiles.crear("span", "fc-secundario");
      datos.appendChild(principal);
      datos.appendChild(secundario);

      cuerpo.appendChild(pista);
      cuerpo.appendChild(datos);
      fila.appendChild(clase);
      fila.appendChild(cuerpo);
      contenedor.appendChild(fila);

      return {
        algoritmo: algoritmo,
        nodo: fila,
        relleno: relleno,
        principal: principal,
        secundario: secundario,
      };
    });
  }

  /**
   * `calcular(algoritmo)` devuelve `{ log10Peso, principal, secundario, destacado }`.
   * El peso llega ya en logaritmo porque 2ⁿ y n! desbordan cualquier número
   * representable: así la barra sigue teniendo sentido con n = 1000.
   */
  FilasComplejidad.prototype.actualizar = function (calcular) {
    const valores = this.filas.map(function (fila) {
      return calcular(fila.algoritmo);
    });

    let minimo = Infinity;
    let maximo = -Infinity;
    valores.forEach(function (valor) {
      if (!isFinite(valor.log10Peso)) return;
      minimo = Math.min(minimo, valor.log10Peso);
      maximo = Math.max(maximo, valor.log10Peso);
    });
    if (!isFinite(minimo)) {
      minimo = 0;
      maximo = 1;
    }
    const rango = Math.max(maximo - minimo, 1);

    this.filas.forEach(function (fila, indice) {
      const valor = valores[indice];
      const peso = isFinite(valor.log10Peso) ? valor.log10Peso : maximo;
      const proporcion = (peso - minimo) / rango;
      fila.relleno.style.width =
        (2 + 98 * utiles.limitar(proporcion, 0, 1)).toFixed(2) + "%";
      fila.principal.textContent = valor.principal;
      fila.secundario.textContent = valor.secundario || "";
      fila.nodo.classList.toggle("es-destacada", !!valor.destacado);
    });
  };

  const PRESUPUESTOS = [
    { etiqueta: "1 segundo", segundos: 1 },
    { etiqueta: "1 minuto", segundos: 60 },
    { etiqueta: "1 hora", segundos: 3600 },
    { etiqueta: "1 día", segundos: 86400 },
    { etiqueta: "1 año", segundos: utiles.SEGUNDOS_POR_ANO },
  ];

  function formatearTamanoMaximo(algoritmo, operaciones) {
    if (!algoritmo.invertir) return "—";
    const n = algoritmo.invertir(operaciones);
    if (!isFinite(n) || n > 1e15) return "cualquiera";
    if (n < 1) return "ni 1";
    if (n < 1000) return Math.floor(n).toLocaleString("es-ES");
    return utiles.formatearCantidad(Math.floor(n));
  }

  /**
   * Tabla "¿hasta dónde llego?": el mayor n que cabe en cada presupuesto de tiempo.
   * Es la forma más clara de ver que lo polinómico escala y lo exponencial no.
   */
  function TablaLimites(contenedor, algoritmos) {
    this.algoritmos = algoritmos;
    const tabla = utiles.crear("table", "tabla");
    const cabecera = utiles.crear("thead");
    const filaCabecera = utiles.crear("tr");
    filaCabecera.appendChild(utiles.crear("th", null, "Complejidad"));
    PRESUPUESTOS.forEach(function (presupuesto) {
      filaCabecera.appendChild(utiles.crear("th", null, presupuesto.etiqueta));
    });
    cabecera.appendChild(filaCabecera);
    tabla.appendChild(cabecera);

    const cuerpo = utiles.crear("tbody");
    this.filas = algoritmos.map(function (algoritmo) {
      const fila = utiles.crear("tr");
      fila.dataset.familia = algoritmo.familia;
      const celdaClase = utiles.crear("th");
      const etiqueta = utiles.crear("span", "punto-clase");
      etiqueta.style.background = algoritmo.color;
      celdaClase.appendChild(etiqueta);
      celdaClase.appendChild(document.createTextNode(" " + algoritmo.clase));
      fila.appendChild(celdaClase);
      const celdas = PRESUPUESTOS.map(function () {
        const celda = utiles.crear("td", "numero", "—");
        fila.appendChild(celda);
        return celda;
      });
      cuerpo.appendChild(fila);
      return { algoritmo: algoritmo, celdas: celdas };
    });
    tabla.appendChild(cuerpo);
    contenedor.innerHTML = "";
    contenedor.appendChild(tabla);
  }

  TablaLimites.prototype.actualizar = function (opsPorSegundo) {
    this.filas.forEach(function (fila) {
      PRESUPUESTOS.forEach(function (presupuesto, indice) {
        const operaciones = opsPorSegundo * presupuesto.segundos;
        fila.celdas[indice].textContent = formatearTamanoMaximo(
          fila.algoritmo,
          operaciones,
        );
      });
    });
  };

  TP.FilasComplejidad = FilasComplejidad;
  TP.TablaLimites = TablaLimites;
  TP.PRESUPUESTOS = PRESUPUESTOS;
})(window);
