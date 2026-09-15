![Tiktokenizer](https://user-images.githubusercontent.com/1443449/222597674-287aefdc-f0e1-491b-9bf9-16431b1b8054.svg)

***

# Tiktokenizer

Online playground for `openai/tiktoken`, calculating the correct number of tokens for a given prompt.

Special thanks to [Diagram](https://diagram.com/) for sponsorship and guidance.

https://user-images.githubusercontent.com/1443449/222598119-0a5a536e-6785-44ad-ba28-e26e04f15163.mp4

---

## 📊 NEW: NumPy & Matplotlib Analysis Environment + Lean Manufacturing MVP

This repository now includes:
1. **Professional plotting and financial analysis environment** with NumPy and Matplotlib
2. **🆕 Interactive Lean Manufacturing Analyzer** MVP in Streamlit

### 🚀 Quick Start (Static Charts)
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 verificar_entorno.py

# Generate your first plot
python3 test_plot.py
```

### 🏭 Quick Start (Lean Manufacturing MVP)
```bash
# Install Lean MVP dependencies
pip install -r requirements_lean.txt

# Run interactive web app
streamlit run lean_streamlit_mvp.py
```

**Or use Google Colab (no installation):** See [QUICKSTART_LEAN.md](QUICKSTART_LEAN.md)

### 📦 What's Included
- ✅ **11 professional chart examples** ready to use
- ✅ **4 Python scripts** (basic, intermediate, and advanced)
- ✅ **Complete documentation** in Spanish
- ✅ **Financial analysis templates**: VPN, DCF, Break-even, Pareto, Sensitivity Analysis
- ✅ **Engineering charts**: Time series, regression, dashboards, cost composition
- ✅ **🆕 Interactive Lean Manufacturing Analyzer**: Lead Time, MUDA detection, VSM, O(n) complexity

### 📖 Documentation
- **[INDEX.md](INDEX.md)** - Complete navigation and overview
- **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - Quick start guide (30 seconds to first plot)
- **[GRAFICOS_README.md](GRAFICOS_README.md)** - Full reference with code examples
- **[RESUMEN_IMPLEMENTACION.md](RESUMEN_IMPLEMENTACION.md)** - Implementation summary
- **🆕 [LEAN_MVP_README.md](LEAN_MVP_README.md)** - **Complete Lean MVP documentation**
- **🆕 [QUICKSTART_LEAN.md](QUICKSTART_LEAN.md)** - **Lean MVP quick start (30 seconds)**

### 🎯 Example Charts Generated
1. Cash flow with break-even analysis
2. NPV sensitivity analysis
3. Project comparison (grouped bars)
4. Time series with trends
5. Scatter plot with linear regression
6. Stacked area (cost composition)
7. Break-even analysis (advanced)
8. Pareto chart (80/20 rule)
9. Discounted cash flow (DCF)
10. Multi-variable sensitivity
11. Executive dashboard (4 metrics)
12. **🆕 Lean Manufacturing interactive analyzer** (Streamlit web app)

See all examples: [View Examples →](INDEX.md)

---

## 🏭 NEW: Lean Manufacturing MVP Features

**Interactive web app for process analysis and waste detection (MUDA)**

### Key Concepts Explained
This MVP clarifies the critical difference between:

- **Lead Time** (Business Metric): Real time from start to finish in your process (e.g., 12 days). An operational metric you experience in the plant.
- **Computational Complexity** (Algorithm Property): Mathematical scale (O(n), O(n²), O(2ⁿ)). Predicts if your algorithm will work with 1M records.

### What It Does
✅ Interactive process editor (editable table like Excel)  
✅ Automatic Lean metrics analysis (Lead Time, Efficiency, MUDA)  
✅ Bottleneck visualization with NetworkX graphs  
✅ Rule-based recommendations (simple if-then logic, no AI)  
✅ O(n) complexity → scales well up to 100k records  

### How to Use
```bash
# Option 1: Local
streamlit run lean_streamlit_mvp.py

# Option 2: Google Colab (no installation)
# See QUICKSTART_LEAN.md for 2-minute setup

# Option 3: Run tests
python3 test_lean_mvp.py

# Option 4: Generate visual demo
python3 generate_lean_demo.py
```

**Demo:** See `lean_mvp_demo_visual.png` for example output

**Full Documentation:** [LEAN_MVP_README.md](LEAN_MVP_README.md)

---

## Acknowledgments

- [T3 Stack](https://create.t3.gg/)
- [shadcn/ui](https://github.com/shadcn/ui)
- [openai/tiktoken](https://github.com/openai/tiktoken)
- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [Streamlit](https://streamlit.io/) - For rapid MVP development
- [NetworkX](https://networkx.org/) - For process flow visualization
- [Lean Enterprise Institute](https://www.lean.org/) - For Lean Manufacturing principles
