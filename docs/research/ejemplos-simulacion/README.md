# Ejemplos de simulación para enseñanza

Scripts Python listos para ejecutar en Jupyter Notebook o Google Colab.

## Archivos

| Script | Descripción | Salida |
| :--- | :--- | :--- |
| `01_lfi_comparacion.py` | Paros antes/después de optimización LFI | `lfi_comparacion.png` |
| `02_secuenciacion_tsp.py` | Secuencia manual vs optimizada (paper TSP) | `secuenciacion_tsp.png` |
| `03_bucle_lfi_lps.py` | Evolución de 30 días con mejora continua | `bucle_lfi_lps.png` |
| `04_flujo_mermaid.mmd` | Diagrama de flujo con marcadores MUDA | Renderizar en GitHub/VS Code |

## Requisitos

```bash
pip install matplotlib numpy
```

## Uso

```bash
cd docs/research/ejemplos-simulacion
python 01_lfi_comparacion.py
python 02_secuenciacion_tsp.py
python 03_bucle_lfi_lps.py
```

Para el diagrama Mermaid, abrir `04_flujo_mermaid.mmd` en VS Code con extensión Mermaid o pegar en GitHub Markdown.
