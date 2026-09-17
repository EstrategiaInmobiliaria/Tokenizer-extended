# Tokenizer-extended — monorepo por dominios

Este repositorio agrupa varios proyectos independientes organizados por dominio.
Cada proyecto conserva su propio `README`, `requirements.txt` y pruebas dentro de
su carpeta; este archivo solo sirve de índice.

| Dominio | Carpeta | Contenido |
|---|---|---|
| Tiktokenizer (app web) | `src/`, `public/`, `package.json` | Playground Next.js/T3 para `openai/tiktoken`. Ver [Tiktokenizer](#tiktokenizer). |
| Finanzas | [`finanzas/`](finanzas/) | Entorno NumPy/Matplotlib (11 gráficos) y Master Blueprint (WACC, DCF, optimización, FastAPI). |
| Inmobiliaria / Læds® | `inmobiliaria/` | Lead scoring, bot WhatsApp + EasyBroker, calculadora Palm Diamante, Meta Ads, Lean MVP, Agartha. *(pendiente de fusionar)* |
| Ingeniería / ciencia | [`ingenieria/`](ingenieria/) | PINNs Navier-Stokes, gemelo digital, solver de optimización, TensorFlow + Power BI, gestión de red de contactos. |
| Docencia | [`docencia/`](docencia/) | Ingeniería industrial, tiempo polinómico, curso RSI 2026, bootloader bare-metal, ejemplos Pascal/C/C++. |
| IA / datos | [`ia/`](ia/) | Knowledge graph y GraphRAG. |

## Convenciones

- **Un `requirements.txt` por proyecto.** No hay `requirements.txt` global: instala el del
  proyecto que vayas a usar (`pip install -r <dominio>/<proyecto>/requirements.txt`).
- **Un solo `.gitignore` en la raíz**, unión de las reglas de todos los proyectos.
- **La home de Next.js (`src/pages/index.tsx`) es Tiktokenizer.** Los frontends de otros
  proyectos viven en rutas propias (`/lead-scoring`, `/palm-diamante`, `/tiempo-polinomico`,
  `/ingenieria-industrial`, `/radar`, …) y no sobrescriben el index.
- Las rutas y scripts de cada proyecto son relativas a su carpeta: entra en ella antes de ejecutarlos.

## Índice de proyectos

### `finanzas/`
- [`graficos-numpy/`](finanzas/graficos-numpy/) — scripts y documentación en español del entorno de gráficos. Empieza por [`INDEX.md`](finanzas/graficos-numpy/INDEX.md); prueba rápida: `cd finanzas/graficos-numpy && ./QUICKTEST.sh`.
- [`master_blueprint/`](finanzas/master_blueprint/) — motor WACC, DCF inmobiliario, optimización lineal, API FastAPI, Docker y tests (`cd finanzas/master_blueprint && pytest tests/`). Resumen: [`MASTER_BLUEPRINT_SUMMARY.md`](finanzas/MASTER_BLUEPRINT_SUMMARY.md).

### `ingenieria/`
- [`navier_stokes_pinns/`](ingenieria/navier_stokes_pinns/) — Physics-Informed Neural Networks para Navier-Stokes (Poiseuille, cavidad).
- [`tensorflow-system/`](ingenieria/tensorflow-system/) — sistema de inteligencia con TensorFlow, API, monitoreo y exportación a Power BI (workflow en `.github/workflows/export-predictions.yml`).
- [`network-management/`](ingenieria/network-management/) — CRM personal: VCF/LinkedIn/Instagram → Supabase + Kùzu, clasificación GPT y flujos n8n para WhatsApp.

### `docencia/`
- [`curso-rsi-2026/`](docencia/curso-rsi-2026/) — video de introducción del curso RSI 2026 (guion, audio, scripts de generación).
- [`bare-metal-bootloader/`](docencia/bare-metal-bootloader/) — bootloader x86 en ensamblador y C con explicación anotada.
- [`ejemplos-programacion/`](docencia/ejemplos-programacion/) — ejemplos comparativos Pascal / C / C++.

### `ia/`
- [`knowledge-graph/`](ia/knowledge-graph/) — ontologías, SPARQL, GraphRAG, ETL de contactos y notebooks.

## Tiktokenizer

![Tiktokenizer](https://user-images.githubusercontent.com/1443449/222597674-287aefdc-f0e1-491b-9bf9-16431b1b8054.svg)

Online playground for `openai/tiktoken`, calculating the correct number of tokens for a given prompt.

Special thanks to [Diagram](https://diagram.com/) for sponsorship and guidance.

https://user-images.githubusercontent.com/1443449/222598119-0a5a536e-6785-44ad-ba28-e26e04f15163.mp4

```bash
yarn install
cp .env.example .env   # HF_API_KEY es opcional
yarn dev
```

### Acknowledgments

- [T3 Stack](https://create.t3.gg/)
- [shadcn/ui](https://github.com/shadcn/ui)
- [openai/tiktoken](https://github.com/openai/tiktoken)
