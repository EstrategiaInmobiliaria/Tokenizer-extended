# 📊 Entorno de Análisis y Graficación con NumPy y Matplotlib

**Instalación completa y ejemplos profesionales listos para usar**

---

## 🎯 ¿Qué incluye este entorno?

Este repositorio proporciona un entorno completo de análisis y visualización financiera/ingenieril con:

- ✅ Scripts de instalación automática
- ✅ 11 ejemplos de gráficos profesionales listos para ejecutar
- ✅ Plantillas personalizables para casos de uso comunes
- ✅ Documentación completa en español
- ✅ Guías de solución de problemas

---

## 🚀 Inicio Rápido (3 comandos)

```bash
# 1. Instalar librerías
pip install -r requirements.txt

# 2. Verificar instalación
python3 verificar_entorno.py

# 3. Generar primer gráfico
python3 test_plot.py
```

---

## 📂 Estructura de Archivos

### 📜 Scripts de Ejecución
| Archivo | Descripción | Gráficos |
|---------|-------------|----------|
| `verificar_entorno.py` | Verifica que todo está instalado correctamente | 0 |
| `test_plot.py` | Script de prueba básico (plantilla inicial) | 1 |
| `ejemplos_graficos.py` | Ejemplos intermedios de visualización | 5 |
| `ejemplos_avanzados.py` | Análisis financieros avanzados completos | 5 |

### 📖 Documentación
| Archivo | Contenido |
|---------|-----------|
| `INICIO_RAPIDO.md` | Guía de instalación y primeros pasos (léelo primero) |
| `GRAFICOS_README.md` | Documentación completa con ejemplos de código |
| `INDEX.md` | Este archivo (índice general) |
| `requirements.txt` | Dependencias del proyecto |

### 📊 Gráficos Generados

#### Nivel Básico (1 gráfico)
- `grafica_prueba.png` - Flujo de caja con punto de equilibrio

#### Nivel Intermedio (5 gráficos)
- `vpn_sensibilidad.png` - Análisis de sensibilidad del VPN
- `comparacion_proyectos.png` - Comparación de proyectos con barras
- `serie_tiempo_produccion.png` - Series temporales con tendencia
- `dispersion_regresion.png` - Análisis de correlación lineal
- `area_apilada_costos.png` - Composición de costos apilada

#### Nivel Avanzado (5 gráficos)
- `break_even_analysis.png` - Análisis completo de punto de equilibrio
- `pareto_chart.png` - Diagrama de Pareto (regla 80/20)
- `dcf_analysis.png` - Flujo de caja descontado (DCF)
- `sensitivity_analysis.png` - Análisis de sensibilidad multivariable
- `executive_dashboard.png` - Dashboard ejecutivo con 4 métricas

---

## 🎓 Ruta de Aprendizaje Recomendada

### 1️⃣ Verificación (2 minutos)
```bash
python3 verificar_entorno.py
```
Confirma que NumPy y Matplotlib están correctamente instalados.

### 2️⃣ Primer Gráfico (5 minutos)
```bash
python3 test_plot.py
```
Genera tu primer gráfico y entiende la estructura básica.

### 3️⃣ Ejemplos Intermedios (15 minutos)
```bash
python3 ejemplos_graficos.py
```
Explora 5 tipos diferentes de visualizaciones.

### 4️⃣ Análisis Avanzados (30 minutos)
```bash
python3 ejemplos_avanzados.py
```
Estudia casos de uso reales de ingeniería económica.

### 5️⃣ Personalización (tu tiempo)
- Abre los archivos `.py` en tu editor
- Modifica datos, colores, títulos
- Experimenta con las plantillas
- Lee `GRAFICOS_README.md` para técnicas avanzadas

---

## 💡 Casos de Uso Incluidos

### Finanzas & Economía
- ✅ Análisis de Valor Presente Neto (VPN)
- ✅ Punto de equilibrio (Break-even)
- ✅ Flujo de caja descontado (DCF)
- ✅ Análisis de sensibilidad
- ✅ ROI por proyectos

### Ingeniería & Operaciones
- ✅ Diagrama de Pareto (80/20)
- ✅ Series temporales con tendencias
- ✅ Análisis de regresión lineal
- ✅ Composición de costos
- ✅ Dashboards ejecutivos

---

## 🔧 Tecnologías Utilizadas

| Librería | Versión Mínima | Propósito |
|----------|----------------|-----------|
| **NumPy** | 1.20.0 | Cálculos numéricos y operaciones vectorizadas |
| **Matplotlib** | 3.3.0 | Generación de gráficos de calidad publicación |
| **Python** | 3.8+ | Lenguaje base |

---

## 📖 Comandos Útiles

### Generar todos los gráficos
```bash
python3 test_plot.py && python3 ejemplos_graficos.py && python3 ejemplos_avanzados.py
```

### Reinstalar librerías
```bash
pip install --upgrade numpy matplotlib
```

### Ver gráficos generados
```bash
ls -lh *.png
```

### Limpiar archivos de prueba
```bash
rm -f *.png test_verificacion.png
```

---

## 🆘 Solución de Problemas

### "ModuleNotFoundError: No module named 'numpy'"
```bash
pip install numpy matplotlib
```

### "Permission denied"
```bash
pip install --user numpy matplotlib
```

### "RuntimeError: Invalid DISPLAY variable"
Agrega al inicio de tus scripts:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
```

### Más ayuda
Consulta la sección de solución de problemas en `GRAFICOS_README.md`

---

## 🌟 Características Destacadas

- 📊 **11 gráficos profesionales** listos para usar
- 🎨 **Estilos personalizables** con paletas de colores profesionales
- 📈 **Casos reales** de análisis financiero e ingeniería
- 📝 **Documentación completa** en español
- ✅ **Scripts verificados** que funcionan out-of-the-box
- 🔧 **Código limpio** y bien comentado
- 🚀 **Instalación en 30 segundos**

---

## 📚 Recursos Adicionales

### Documentación Oficial
- [NumPy Documentation](https://numpy.org/doc/stable/)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)

### Tutoriales
- [NumPy Quickstart](https://numpy.org/doc/stable/user/quickstart.html)
- [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html)

---

## 🎯 Próximos Pasos

1. ✅ Lee `INICIO_RAPIDO.md` para comenzar
2. ✅ Ejecuta `verificar_entorno.py` para validar tu instalación
3. ✅ Genera tus primeros gráficos con los scripts incluidos
4. ✅ Estudia el código en los archivos `.py`
5. ✅ Personaliza las plantillas con tus propios datos
6. ✅ Consulta `GRAFICOS_README.md` para técnicas avanzadas

---

## 📄 Licencia

Este entorno está diseñado para uso educativo y profesional. Siéntete libre de modificar y adaptar los ejemplos según tus necesidades.

---

## 🤝 ¿Necesitas Ayuda?

Para casos de uso específicos o personalizaciones avanzadas:
1. Revisa los ejemplos incluidos
2. Consulta la documentación oficial
3. Experimenta con las plantillas proporcionadas

---

**¡Comienza a crear visualizaciones profesionales ahora! 📊🚀**

```bash
python3 verificar_entorno.py
```
