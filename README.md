<div align="center">

# 🧠 DSA Practice — GFG 2026

**A structured, notebook-based Data Structures & Algorithms practice repository**  
built alongside [GeeksforGeeks](https://www.geeksforgeeks.org/), with built-in complexity analysis on every solution.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?style=flat-square&logo=jupyter&logoColor=white)
![GFG](https://img.shields.io/badge/GeeksforGeeks-2026-2F8D46?style=flat-square&logo=geeksforgeeks&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

</div>

---

## ✨ What Makes This Repo Special

Every notebook cell automatically reports:

| Feature | Description |
|---|---|
| 🏷️ **Big-O Badges** | Time & Space complexity detected via static AST analysis |
| 📝 **Why Breakdown** | Human-readable notes explaining the complexity verdict |
| ⏱️ **Actual Runtime** | Wall-clock time in milliseconds for the cell execution |
| 🧮 **Peak Memory** | Tracemalloc-measured peak memory in KB |
| 🔕 **Opt-out** | Add `# NO_ANALYZE` as the first line of any cell to skip |

This is powered by the custom **`utils/complexity_runner.py`** engine — a zero-dependency tool that hooks into IPython's cell execution pipeline.

---

## 📁 Repository Structure

```
dsa-gfg-2026/
│
├── 01_Logic_Building/              # Section 1 — Foundation & Logic
│   └── 01_Basic_Problems/          # Core building-block problems
│       ├── 01_Check_Even_or_Odd.ipynb
│       ├── 02_Multiplication_Table.ipynb
│       └── 03_Sum_of_Naturals.ipynb
│
├── utils/                          # Shared tooling
│   ├── complexity_runner.py        # Auto Big-O analyzer + runtime profiler
│   └── __init__.py
│
└── assets/                         # Screenshots & media
```

> More sections will be added as practice progresses (Arrays, Strings, Recursion, Sorting, etc.)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/dsa-gfg-2026.git
cd dsa-gfg-2026
```

### 2. Set Up the Python Environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
pip install jupyter ipython
```

### 3. Launch Jupyter

```bash
jupyter notebook
# or open the .ipynb files directly in VS Code
```

### 4. Activate the Complexity Runner

Every notebook has this **setup cell** at the top — just run it once per session:

```python
# NO_ANALYZE
import sys, os

_root = os.path.abspath(os.getcwd())
for _ in range(6):
    if os.path.exists(os.path.join(_root, "utils", "complexity_runner.py")):
        break
    _root = os.path.dirname(_root)

if _root not in sys.path:
    sys.path.insert(0, _root)

from utils.complexity_runner import setup_complexity_runner
setup_complexity_runner()
```

After that, **every cell you run** will automatically display its complexity analysis.

---

## 📓 Notebook Format

Each problem notebook follows a consistent, readable structure:

```
Problem Title
│
├── [Naive Approach]       — Simple brute-force, O(n) or worse
│   └── Code + auto complexity output
│
├── [Alternative Approach] — Improved method (e.g. Recursion)
│   └── Code + auto complexity output
│
└── [Expected Approach]    — Optimal solution with best complexity
    └── Code + auto complexity output
```

---

## 🗂️ Problems Index

### 01 · Logic Building

| # | Problem | Approaches Covered | Best Complexity |
|---|---|---|---|
| 01 | Check Even or Odd | Modulo, Bitwise | O(1) Time · O(1) Space |
| 02 | Multiplication Table | Loop, Recursion | O(n) Time · O(1) Space |
| 03 | Sum of Natural Numbers | Loop, Recursion, Formula | **O(1) Time · O(1) Space** |

---

## 🛠️ Utils — `complexity_runner.py`

A custom IPython extension that performs **static AST analysis** on every cell:

- Detects **loop depth** → maps to O(1), O(n), O(n²), O(n³) …
- Detects **binary search patterns** → O(log n)
- Detects **recursion** (including constant-bounded recursion) → O(n) or O(log n)
- Detects **sort / sorted calls** → O(n log n)
- Detects **dynamic data structures** (list, dict, set literals) → O(n) space
- Measures **actual wall-clock time** (via `time.perf_counter`)
- Measures **peak memory** (via `tracemalloc`)

To skip analysis on any cell, place `# NO_ANALYZE` on the **first line**.

---

## 🤝 Contributing

This is a personal practice repository, but suggestions and improvements are welcome!

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/new-problem`
3. Commit your changes: `git commit -m "Add: binary search notebook"`
4. Push and open a Pull Request

---

## 📜 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).  
Problem statements belong to their respective owners at [GeeksforGeeks](https://www.geeksforgeeks.org/).

---

<div align="center">

Made with ❤️ for consistent DSA practice · Updated 2026

</div>
