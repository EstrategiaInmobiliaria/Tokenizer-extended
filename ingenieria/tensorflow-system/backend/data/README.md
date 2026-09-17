# Estructura de Datos

Este directorio contiene los datasets para entrenamiento y re-entrenamiento de modelos.

## Formato de Datos

### 1. Inmobiliario

**Archivo**: `real_estate/training_data.csv`

**Columnas**:
- `desarrollo`: Nombre del desarrollo (string)
- `precio_m2`: Precio por metro cuadrado (float, 25000-75000)
- `ubicacion`: Ciudad/zona (string: Querétaro, CDMX, Monterrey, etc.)
- `amenidades`: Cantidad de amenidades (int, 0-20)
- `velocidad_ventas`: Velocidad de ventas actual (float, 0-1)
- `cap_rate`: Tasa de capitalización (float, 4-10%)
- `vendido_12_meses`: Se vendió en 12 meses (int, 0 o 1)
- `precio_venta_real`: Precio final de venta (float)
- `dias_venta`: Días que tardó en venderse (int, 90-730)

**Ejemplo**:
```csv
desarrollo,precio_m2,ubicacion,amenidades,velocidad_ventas,cap_rate,vendido_12_meses,precio_venta_real,dias_venta
Torre Central,45000,Querétaro,12,0.85,7.2,1,18500000,156
```

**Fuentes recomendadas**:
- Softec (si tienes acceso)
- Google Sheets con análisis manual
- CSV exportado de Power BI

---

### 2. Redes Sociales

**Archivo**: `social_media/instagram_posts.csv`

**Columnas**:
- `fecha`: Fecha y hora publicación (datetime, ISO 8601)
- `tipo_contenido`: Tipo de post (string: Carrusel, Reel, Story, Post)
- `tema_categoria`: Tema del contenido (string)
- `hora_publicacion`: Hora del día (int, 0-23)
- `num_hashtags`: Cantidad de hashtags (int, 0-30)
- `longitud_caption`: Longitud del caption en caracteres (int)
- `likes`: Cantidad de likes (int)
- `guardados`: Cantidad de guardados (int)
- `comentarios`: Cantidad de comentarios (int)
- `shares`: Cantidad de compartidos (int)
- `alcance`: Alcance total (int)

**Ejemplo**:
```csv
fecha,tipo_contenido,tema_categoria,hora_publicacion,num_hashtags,longitud_caption,likes,guardados,comentarios,shares,alcance
2024-01-15 09:00:00,Reel,Cap Rate,9,5,150,847,89,34,12,4235
```

**Fuentes recomendadas**:
- Instagram Insights API (via n8n)
- Meta Business Suite exportación manual
- Hootsuite/Buffer analytics

---

### 3. Personal - TCO

**Archivo**: `personal/auto_costs.csv`

**Columnas**:
- `modelo`: Modelo del vehículo (string)
- `precio_inicial`: Precio de compra (float)
- `gasolina_mensual`: Costo mensual gasolina (float)
- `seguro_anual`: Costo seguro anual (float)
- `mantenimiento_anual`: Costo mantenimiento anual (float)
- `depreciacion_anual`: Depreciación anual (float)
- `km_anuales`: Kilometraje anual (int)
- `rendimiento_km_l`: Rendimiento km/litro (float)
- `es_electrico`: Es híbrido/eléctrico (int, 0 o 1)

**Ejemplo**:
```csv
modelo,precio_inicial,gasolina_mensual,seguro_anual,mantenimiento_anual,depreciacion_anual,km_anuales,rendimiento_km_l,es_electrico
Geely EX5 EM-i,650000,800,12000,8000,65000,20000,25,1
```

**Fuentes recomendadas**:
- Registro manual de gastos
- App de finanzas personales
- Excel de control de gastos

---

### 4. Personal - Tenis

**Archivo**: `personal/tennis_matches.csv`

**Columnas**:
- `tension_cordaje`: Tensión del cordaje en kg (int, 20-28)
- `tipo_pelota_encoded`: Tipo de pelota (int, 0-2)
  - 0: Wilson US Open
  - 1: Penn Championship
  - 2: Dunlop ATP
- `temperatura`: Temperatura ambiente en °C (int, 10-40)
- `rival_nivel`: Nivel del rival (int, 1-10)
- `dia_semana`: Día de la semana (int, 0-6)
- `horas_descanso`: Días de descanso previos (int, 0-3)
- `victoria`: Resultado (int, 0 o 1)

**Ejemplo**:
```csv
tension_cordaje,tipo_pelota_encoded,temperatura,rival_nivel,dia_semana,horas_descanso,victoria
24,0,24,6,1,2,1
```

**Fuentes recomendadas**:
- Registro manual post-partido
- App de tenis (PlayYourCourt, Tennis Record)
- Notas en Obsidian

---

## Re-entrenamiento

### Cuándo re-entrenar

Re-entrena un modelo cuando:
1. Acumules +50 nuevos datos
2. Mensualmente (mínimo)
3. La accuracy caiga <80%

### Cómo agregar datos

**Opción 1: Agregar al CSV**

```bash
# Agregar una línea al CSV existente
echo "Torre Norte,48000,CDMX,14,0.78,6.9,1,22500000,178" >> data/real_estate/training_data.csv

# Re-entrenar
python backend/scripts/train_all_models.py
```

**Opción 2: Reemplazar CSV completo**

```bash
# Guardar backup
cp data/real_estate/training_data.csv data/real_estate/training_data_backup_$(date +%Y%m%d).csv

# Reemplazar con nuevo CSV
cp /path/to/new_data.csv data/real_estate/training_data.csv

# Re-entrenar
python backend/scripts/train_all_models.py
```

**Opción 3: Vía API** (próximamente)

```python
import requests

requests.post('http://localhost:3001/api/admin/retrain', json={
    'model': 'real_estate_opportunity',
    'new_data': [...]
})
```

---

## Validación de Datos

Antes de re-entrenar, valida que tu CSV:

1. **No tenga valores nulos**:
   ```python
   import pandas as pd
   df = pd.read_csv('data/real_estate/training_data.csv')
   print(df.isnull().sum())
   ```

2. **Tenga el formato correcto**:
   ```python
   # Verificar columnas
   expected_cols = ['desarrollo', 'precio_m2', 'ubicacion', ...]
   assert all(col in df.columns for col in expected_cols)
   ```

3. **Tenga suficientes datos**:
   ```python
   print(f"Total rows: {len(df)}")
   assert len(df) >= 100  # Mínimo recomendado
   ```

---

## Privacidad de Datos

**Importante**: Los datos de este directorio son privados. Asegúrate de:

1. **No commitear datos reales**:
   ```bash
   # Los CSV están en .gitignore
   git status  # Verificar que no aparezcan
   ```

2. **Encriptar backups**:
   ```bash
   # Antes de guardar en cloud
   tar -czf data_backup.tar.gz data/
   gpg -c data_backup.tar.gz
   ```

3. **Anonimizar datos sensibles**:
   ```python
   # Reemplazar nombres reales
   df['desarrollo'] = df['desarrollo'].apply(lambda x: f"DEV-{hash(x) % 1000:03d}")
   ```

---

## FAQ

**P: ¿Cuántos datos necesito para empezar?**
R: Mínimo 100 por modelo, ideal 200+. El sistema viene con datos de ejemplo para probar.

**P: ¿Puedo mezclar datos reales con sintéticos?**
R: Sí, pero mantén ratio 80% reales / 20% sintéticos.

**P: ¿Los datos de ejemplo son buenos?**
R: Son suficientes para probar el sistema, pero debes reemplazarlos con tus datos reales para predicciones precisas.

**P: ¿Cómo limpio datos corruptos?**
R: 
```python
df = df.dropna()  # Eliminar nulos
df = df.drop_duplicates()  # Eliminar duplicados
df = df[df['precio_m2'] > 0]  # Eliminar inválidos
```

**P: ¿Puedo exportar datos de Softec directamente?**
R: Sí, exporta a CSV y mapea las columnas al formato esperado.
