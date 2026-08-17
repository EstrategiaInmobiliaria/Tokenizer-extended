# 2. Diagramas de flujo: los procesos del libro esquematizados

> Fuente: caps. 1, 2, 6 y 7 de la 2.ª edición. Simbología y taxonomía de diagramas: cap. 7, «Estudio de
> métodos» (pp. 176–185). Verificado contra el texto.

El punto de partida es la tesis del capítulo 1: la empresa debe verse como **una serie de procesos**
interrelacionados por los que fluyen sin parar tres elementos —información, dinero y materia prima—,
igual que el cuerpo humano hace circular información genética, gases y nutrientes `[C1 · p. 11]`.

## Simbología ASME para diagramas de proceso

La simbología «fue generada por la Asociación de Ingenieros Mecánicos de Estados Unidos de América, por
lo que es estándar y permite que el mismo diagrama sea entendido por analistas en cualquier parte del
mundo» `[C7 · p. 177]`.

| Símbolo | Nombre | Qué representa | Ejemplos del libro |
| --- | --- | --- | --- |
| ○ círculo | **Operación** (o acción) | Actividades fundamentales que propician cambios en materiales u objetos, transferencia de información o planeación de algo | Clavar con martillo, tornear una pieza, barrenar una placa, dibujar un plano, teclear en la computadora |
| → flecha | **Transporte** | Personas, materiales o equipo se trasladan **sin** que se les efectúe trabajo adicional | Transportar material en carretilla, elevar objetos con poleas, llevar documentos de un escritorio a otro |
| □ cuadrado | **Inspección** | Verificación de calidad o cantidad, y lecturas de indicadores o de información impresa | Contar piezas de un depósito, inspección de calidad, leer manómetros de tanques |
| D semicircular | **Demora** | Interferencias en el flujo, imposibilidad de pasar al siguiente paso, trabajo en suspenso o abandono momentáneo | Espera en ascensores, cuellos de botella en una máquina, documentos que aguardan su archivo |
| ▽ triángulo invertido | **Almacenamiento** | Depósito del material o producto en algún lugar, idealmente almacenes | Materia prima, producto en proceso, producto terminado, papel moneda en caja de seguridad |
| símbolos combinados | **Actividades combinadas** | Dos actividades ejecutadas simultáneamente; la más común es operación-inspección | Verificar mientras se ensambla |

Dos advertencias del texto que suelen preguntarse:

- La **inspección** «por lo general no añade valor al producto, por lo que se deberá ser muy crítico en
  su existencia» `[C7 · p. 177]`.
- El **almacenamiento** debería ocurrir en almacenes, «aunque es probable que en el método actual se
  encuentren mercancías almacenadas en pisos o pasillos por error» `[C7 · p. 178]`.

Equivalencia con las formas de Mermaid, para que puedas dibujar los diagramas en texto (Mermaid no
tiene el círculo, la «D» ni el triángulo invertido de la norma, así que se aproximan):

```mermaid
flowchart LR
    OP(("Operación<br/>círculo"))
    TR>"Transporte<br/>flecha"]
    IN["Inspección<br/>cuadrado"]
    DE(["Demora<br/>letra D"])
    AL[\"Almacenamiento<br/>triángulo invertido"/]
    CO{{"Combinada<br/>operación-inspección"}}

    OP --> TR --> IN --> DE --> AL --> CO
```

## Las tres familias de diagramas de análisis de proceso

El capítulo 7 clasifica los diagramas en tres familias; conocer la clasificación evita el error típico de
llamar «diagrama de flujo» a todo `[C7 · pp. 178–184]`.

```mermaid
flowchart TD
    R["Diagramas de análisis de proceso<br/>simbología ASME"]

    R --> F1["1. Indican secuencias<br/>de operaciones"]
    R --> F2["2. Poseen escalas<br/>de tiempo"]
    R --> F3["3. Representan flujo,<br/>movimiento o desplazamiento"]

    F1 --> A1["Cursograma sinóptico del proceso<br/>vista general y resumida<br/>fig. 7.3"]
    F1 --> A2["Cursograma analítico<br/>detalle paso a paso, con tiempos y distancias<br/>versiones de operario, material y equipo<br/>fig. 7.4"]
    F1 --> A3["Diagrama bimanual<br/>actividades de ambas manos en un área pequeña<br/>fig. 7.5"]

    F2 --> B1["Diagrama de actividades múltiples<br/>hombre-máquina<br/>detecta y cuantifica tiempos muertos<br/>fig. 7.6"]

    F3 --> C1["Diagrama de recorrido<br/>planta a escala con flujos y distancias<br/>complementa el cursograma analítico<br/>fig. 7.7"]
    F3 --> C2["Diagrama de hilos<br/>intensidad de relación entre áreas"]
```

Detalles que el texto pide no olvidar:

- El **cursograma analítico** ordena los símbolos siempre igual: operaciones, transportes, demoras,
  inspecciones y almacenajes; incluye encabezado (versión, trabajo, método actual o propuesto, fecha,
  lugar, autoría) y un **resumen** con totales de cada actividad, distancias y tiempos `[C7 · pp. 178–180]`.
- La línea quebrada que une las actividades es un diagnóstico visual: si «la línea estará más cargada
  hacia la derecha» hay muchas actividades que no agregan valor y se debe pasar de inmediato al análisis
  crítico `[C7 · p. 180]`.
- En el diagrama **hombre-máquina** el rectángulo blanco es inactividad, el negro es operación
  independiente y el gris es actividad simultánea `[C7 · pp. 182–183]`.

Plantilla mínima del cursograma analítico, para copiar en el cuaderno:

| # | Descripción del elemento | ○ | → | D | □ | ▽ | Tiempo (min) | Distancia (m) | Observaciones |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | | | | |
| 2 | | | | | | | | | |
| | **Resumen (totales)** | | | | | | | | |

## 1. Los tres flujos de la empresa (capítulo 1)

Tres diagramas de bloque sobre los mismos departamentos. El libro advierte que para «ver viva» a la
industria hay que **unir las tres figuras en una sola** e imaginar la información fluyendo sin parar,
mientras el dinero y los materiales fluyen más lento `[C1 · p. 15]`.

### 1.1 Flujo de información (figura 1.1, p. 12)

La dirección general es el óvalo del diagrama: «se puede considerar el cerebro del suprasistema, pues es
la única entidad que debe tener información en ambos sentidos» `[C1 · p. 12]`. El ciclo no tiene
principio: «los suprasistemas viven e intercambian información de manera permanente» `[C1 · p. 12]`.

```mermaid
flowchart TD
    CONS["Consumidores actuales<br/>y potenciales"]
    MERC["Investigación<br/>de mercado"]
    DG(["Administración de la empresa<br/>dirección general<br/>el cerebro del suprasistema"])
    ACC["Propietarios o<br/>accionistas"]
    GOB["Gobierno<br/>impuestos y seguridad social"]
    MACRO["Información macroeconómica<br/>banco central y cámaras"]
    TEC["Uso de la tecnología<br/>y diseño del producto"]
    CONT["Contabilidad<br/>y finanzas"]
    RH["Recursos humanos"]
    PROV["Proveedores de<br/>materia prima"]
    ALMP["Almacén de<br/>materia prima"]
    PROD["Elaboración del producto<br/>producción"]
    ALPT["Almacén de<br/>producto terminado"]
    DIST["Distribución y ventas"]
    SAT["Satisfacción y<br/>atención al cliente"]

    CONS -->|"necesidades detectadas"| MERC
    MERC -->|"nuevas necesidades y clientes potenciales"| DG
    SAT -->|"quejas y necesidades de clientes actuales"| DG
    DG -->|"mantener o cambiar diseño y tecnología"| TEC
    TEC -->|"recursos requeridos para el cambio"| CONT
    CONT -->|"disponibilidad de recursos o fuente de fondeo"| DG
    DG <-->|"informes de desempeño y decisiones"| ACC
    DG <-->|"obligaciones fiscales y laborales"| GOB
    MACRO -->|"contexto para decidir"| DG
    DG <-->|"contexto para decidir"| ACC

    DIST -->|"cantidades requeridas por el mercado"| PROD
    PROD -->|"cantidad y fecha de materia prima"| ALMP
    ALMP -->|"pedido"| PROV
    PROV <-->|"especificaciones de calidad"| PROD
    ALMP -->|"pasivos por compra y costo de producción"| CONT
    CONT -->|"aviso de pago realizado"| PROV
    ALMP -->|"entrega programada"| PROD
    PROD -->|"producto disponible en tiempo y forma"| DIST
    PROD --> ALPT
    ALPT -->|"existencias"| CONT
    DIST -->|"sitios, cantidades y frecuencias de entrega"| CONS
    DIST -->|"operación realizada y fecha de cobro"| CONT
    CONS -->|"pago al vencimiento"| CONT
    RH <-->|"faltas, retardos, sueldos, prestaciones"| CONT
    CONT -->|"resultados del periodo"| DG
```

Preguntas de control sobre esta figura: ¿por qué la información entre producción y proveedores es de
doble sentido? (control de especificaciones de calidad). ¿Por qué contabilidad conversa con recursos
humanos? (faltas, retardos, sueldos, promociones, prestaciones y jubilaciones) `[C1 · pp. 13–14]`.

### 1.2 Flujo de dinero (figura 1.2, p. 14)

Clave de lectura: «Contabilidad es la única que distribuye y recibe dinero, dentro y fuera de la
empresa» y en varias flechas «no hay flujo de dinero real entre áreas», sino **movimientos contables**
`[C1 · p. 14]`.

```mermaid
flowchart LR
    CONT(["Contabilidad y finanzas<br/>único punto de entrada y salida de dinero"])

    VTAS["Distribución del producto<br/>al consumidor"]
    BANCO["Fuentes de financiamiento<br/>bancos"]
    ACC["Propietarios o<br/>accionistas"]
    GOB["Gobierno<br/>impuestos y cuotas"]
    PROV["Proveedores de materia<br/>prima e insumos"]
    EST["Estudios especiales<br/>dentro o fuera de la empresa"]
    RH["Recursos humanos<br/>nómina y prestaciones"]
    TEC["Uso de tecnología<br/>en la empresa"]
    PROD["Producción"]
    ALM["Almacenes de materia prima<br/>y de producto terminado"]

    VTAS -->|"ingreso principal por ventas"| CONT
    CONT -->|"devoluciones, bonificaciones y descuentos por pronto pago"| VTAS
    BANCO <-->|"crédito y servicio de la deuda"| CONT
    ACC <-->|"aportaciones de capital y reparto de utilidades"| CONT
    CONT -->|"impuestos y seguridad social"| GOB
    CONT -->|"pago de materia prima, energía, teléfono, internet"| PROV
    CONT -->|"honorarios"| EST
    CONT -->|"sueldos y prestaciones"| RH
    CONT -->|"compra de tecnología y equipo"| TEC
    CONT -->|"1 cambio de tecnología"| PROD
    CONT -->|"2 tecnología anticontaminante"| PROD
    CONT -->|"3 mantenimiento preventivo y correctivo"| PROD
    CONT -->|"4 pruebas de calidad"| PROD
    ALM -.->|"movimiento contable por cada entrada y salida, y por obsolescencia"| CONT
```

Las **cuatro razones** por las que contabilidad envía dinero a producción son materia de examen: cambio
de tecnología, control de la contaminación, mantenimiento y pruebas de calidad `[C1 · pp. 14–15]`. El
ejemplo de obsolescencia del libro: la leche fresca tiene vida de almacén de dos o tres días; pasada
esa fecha se da de baja física y contablemente `[C1 · p. 14]`.

### 1.3 Flujo de materia prima e insumos (figura 1.3, p. 15)

La idea central: cada proceso, «por simple que éste sea», **agrega valor**; el ejemplo del libro es el
frijol a granel frente al frijol envasado en bolsas de 1 kg `[C1 · p. 13]`.

```mermaid
flowchart LR
    PROV["Proveedores de materia<br/>prima e insumos"] --> ALMP[\"Almacén de<br/>materia prima"/]
    ALMP --> PROD(("Producción<br/>transformación que<br/>agrega valor"))
    PROD --> P["Producto terminado"]
    PROD --> S["Subproductos<br/>desechos con valor comercial"]
    PROD --> D["Desechos contaminantes<br/>generan costo adicional"]
    P --> ALPT[\"Almacén de<br/>producto terminado"/]
    ALPT --> DIST["Distribución<br/>logística"]
    DIST --> CONS["Consumidor"]
    S --> OTRAS["Otras industrias<br/>como materia prima"]
    D --> ANTI["Tecnología<br/>anticontaminante"]

    subgraph EJ["Ejemplos del libro"]
        direction TB
        E1["Jugo de limón: la cáscara da pectina<br/>y las semillas dan limonoides<br/>subproductos de alto valor"]
        E2["Pintado de carrocerías: metal en el agua<br/>de lavado y solventes en la atmósfera<br/>desechos contaminantes"]
    end
```

Distinción que el capítulo remarca: comprar tecnología (maquinaria, fórmulas, planos) es una cosa;
**usarla eficientemente** es otra, y «en esta distinción, que puede parecer sutil, radica la esencia de
la ingeniería industrial» `[C1 · p. 15]`.

## 2. Representación general de un proceso industrial (capítulo 2)

Figura 2.5, p. 32. El esquema entradas → proceso transformador → salidas, con la distinción entre
**operación unitaria** (cambio físico) y **proceso unitario** (cambio químico).

```mermaid
flowchart LR
    A["A · Materias primas"] --> T
    B["B · Agua"] --> T
    C["C · Aire"] --> T
    D["D · Combustibles"] --> T

    subgraph T["Proceso transformador"]
        direction LR
        OU1["Operación unitaria<br/>cambio físico"] --> PU["Proceso unitario<br/>reacción química"] --> OU2["Operación unitaria<br/>cambio físico"]
    end

    T --> P["P · Producto"]
    T --> S["S · Subproducto"]
    T --> EG["EG · Emisiones gaseosas"]
    T --> AR["AR · Aguas residuales"]
    T --> R["R · Residuos"]
```

Al dibujarlo, agrega en el margen las operaciones unitarias que el capítulo desarrolla, porque son la
lista de verificación de cualquier proceso: transporte de materiales, bombeo de líquidos y gases,
compresión de gases, reducción de tamaño (quebrantado, trituración, molienda), transferencia de calor,
mezclado y operaciones de separación —destilación, evaporación, secado, filtración, centrifugación y
tamizado— `[C2 · pp. 39–43]`.

## 3. Proceso de administración de proyectos (capítulo 6)

Figura 6.8, p. 145. Ocho pasos, del desglose de tareas al aprendizaje organizacional.

```mermaid
flowchart TD
    P1["1. Identificar las operaciones<br/>o tareas del proyecto<br/>con inicio y fin claros"]
    P2["2. Estimar la duración<br/>de las operaciones"]
    P3["3. Estimar los requerimientos<br/>de recursos<br/>personal, equipo y materiales"]
    P4["4. Preparar presupuestos"]
    P5["5. Supervisar el progreso<br/>en tiempo y en dinero"]
    P6["6. Realizar ajustes a los planes<br/>si es necesario"]
    P7["7. Finalizar el proyecto y evaluar<br/>los resultados obtenidos"]
    P8["8. Generar conocimientos y experiencia<br/>para proyectos futuros"]

    P1 --> P2 --> P3 --> P4 --> P5 --> P6 --> P7 --> P8
    P6 -.->|"replaneación"| P5
    P8 -.->|"lecciones aprendidas"| P1
```

Observación crítica del autor, útil para justificar el paso 5 en un examen: la supervisión estricta del
avance «especialmente en lo referente al dinero… no es una actividad muy frecuente en la administración
de proyectos en Latinoamérica» `[C6 · p. 145]`.

Como caso concreto, el libro esquematiza las fases de implementación de un software de administración de
almacenes (WMS) `[C6 · fig. 6.9 · p. 146]`:

```mermaid
flowchart LR
    F1["Alineación de objetivos<br/>del proveedor con los del cliente"] --> F2["Configuración, modificaciones<br/>y adaptación del software<br/>con validación del cliente"]
    F2 --> F3["Integración, pruebas<br/>e instalación final"]
    F3 --> F4["Capacitación<br/>al usuario final"]
    F4 --> F5["Soporte y ayuda<br/>posinstalación"]
```

Para el **control** del proyecto, el capítulo desarrolla la gráfica de Gantt (actividades en el eje
vertical, escala de tiempo en el horizontal, barras y reglas de precedencia) y el CPM `[C6 · pp. 147–153]`.

## 4. Las seis etapas de un estudio de métodos (capítulo 7)

Figura 7.1, p. 176. El estudio de métodos es «el registro y el examen crítico sistemático que se efectúa
a las maneras de realizar actividades, con el fin de proponer mejoras» `[C7 · p. 176]`.

```mermaid
flowchart TD
    E1["1. Seleccionar<br/>el trabajo a estudiar"]
    E2["2. Registrar<br/>la información pertinente"]
    E3["3. Examinar<br/>los métodos de trabajo"]
    E4["4. Establecer<br/>la evaluación de las opciones"]
    E5["5. Definir<br/>el método más adecuado"]
    E6["6. Implantar<br/>y controlar"]

    E1 --> E2 --> E3 --> E4 --> E5 --> E6
    E6 -.->|"mantener en uso y detectar nuevas prioridades"| E1

    E1 --- N1["Criterios: costo, técnicos y humanos.<br/>Prioridad con análisis de Pareto<br/>o clasificación ABC"]
    E2 --- N2["Observación directa y registro<br/>en papel, video o diagramas<br/>con simbología ASME"]
    E3 --- N3["Análisis crítico: eliminar demoras,<br/>inspecciones y almacenajes<br/>que no agregan valor"]

    N1:::nota
    N2:::nota
    N3:::nota
    classDef nota fill:#f7f7f7,stroke:#bbb,color:#333
```

Detalle de la etapa 1 que conviene memorizar: se atienden primero los trabajos que representan mayor
costo para la empresa —en dinero, distancias o tiempos—, los que involucren cambios de tecnología y los
que ocasionen problemas importantes al empleado; la prioridad se fija con análisis de Pareto (principio
80-20) o clasificación ABC `[C7 · pp. 176–177]`.

### El estudio de métodos dentro del estudio y diseño del trabajo

```mermaid
flowchart TD
    EDT["Estudio y diseño del trabajo<br/>EDT"]
    EDT --> A["1. Estudio de métodos<br/>cómo se hace el trabajo"]
    EDT --> B["2. Medición del trabajo<br/>cuánto tarda"]
    EDT --> C["3. Ergonomía<br/>adaptar el puesto a la persona"]
    EDT --> D["4. Higiene y seguridad industriales<br/>proteger la integridad física"]

    ORIG["Dos corrientes en tensión"]
    ORIG --> T1["Administración científica<br/>Taylor y los Gilbreth<br/>medir y analizar el método"]
    ORIG --> T2["Enfoque sociotécnico<br/>Maslow, Herzberg, McGregor<br/>necesidades y aspiraciones"]
    T1 --> EDT
    T2 --> EDT
```

`[C7 · pp. 175–176]`

### Medición del trabajo (figuras 7.11 y 7.12, pp. 186–188)

```mermaid
flowchart LR
    subgraph PASOS["Pasos de un estudio de medición del trabajo"]
        direction TB
        M1["Registrar información<br/>pertinente"] --> M2["Examinar los<br/>métodos de trabajo"] --> M3["Medir cada elemento<br/>del trabajo"]
    end

    subgraph TEC["Técnicas disponibles"]
        direction TB
        X1["Medición directa<br/>con cronómetro"]
        X2["Muestreo del trabajo"]
        X3["Sistemas de tiempos<br/>predeterminados y MOST"]
        X4["Datos históricos<br/>y datos tipo"]
        X5["Estimaciones hechas<br/>por el analista"]
    end

    PASOS --> TEC
```

Variantes del estudio de tiempos con cronómetro, en orden `[C7 · pp. 187–190]`: seleccionar el trabajo →
seleccionar un operario **calificado** (trabajador promedio, ritmo normal) → analizar el trabajo →
dividirlo en elementos → mediciones de prueba con al menos 20 observaciones iniciales → determinar el
tamaño de muestra con base estadística (la OIT recomienda 95.45 % de confianza).

## Ejercicio propuesto

Elige un proceso que conozcas de primera mano (sacar una impresión en la escuela, preparar un café,
inscribirte a materias) y:

1. Levanta el **cursograma analítico** con la plantilla de arriba, usando los cinco símbolos.
2. Suma cuántas actividades **no agregan valor** (transportes, demoras, inspecciones, almacenajes) y qué
   porcentaje del tiempo total consumen.
3. Aplica la etapa 3 (examinar) y propón un método alternativo; cuantifica el ahorro en tiempo y
   distancia.

Ese ejercicio reproduce, en pequeño, lo que el capítulo 7 llama análisis crítico del proceso, y es la
forma más rápida de fijar la simbología.
