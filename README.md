<div align="center">

# 🧠 DSA Practice — GFG 2026

**A structured, notebook-based Data Structures & Algorithms practice repository**  
built alongside [GeeksforGeeks](https://www.geeksforgeeks.org/), with built-in complexity analysis on every solution.

![Python](https://img.shields.io/badge/Python-3.14-blue?style=flat-square&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?style=flat-square&logo=jupyter&logoColor=white)
![GFG](https://img.shields.io/badge/GeeksforGeeks-2026-2F8D46?style=flat-square&logo=geeksforgeeks&logoColor=white)
![Problems](https://img.shields.io/badge/Problems-10-blueviolet?style=flat-square)
![Approaches](https://img.shields.io/badge/Approaches-25-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

</div>

---

## ✨ What Makes This Repo Special

Every notebook cell **automatically** reports its complexity — no manual annotation needed:

| Feature | Description |
|---|---|
| 🏷️ **Big-O Badges** | Time & Space complexity detected via static AST analysis |
| 📝 **Why Breakdown** | Human-readable notes explaining the complexity verdict |
| ⏱️ **Actual Runtime** | Wall-clock time in milliseconds for the cell execution |
| 🧮 **Peak Memory** | `tracemalloc`-measured peak memory in KB |
| 🔕 **Opt-out** | Add `# NO_ANALYZE` as the first line of any cell to skip |

This is powered by the custom **Complexity Runner** engine (`utils/complexity_runner.py`) — a zero-dependency tool that hooks into IPython's cell execution pipeline.

---

## 📁 Repository Structure

```
dsa-gfg-2026/
│
├── 01_Logic_Building/                       # Section 1 — Foundation & Logic
│   ├── 01_Basic_Problems/                   # Core building-block problems
│   │   ├── 01_Check_Even_or_Odd.ipynb       #   2 approaches
│   │   ├── 02_Multiplication_Table.ipynb    #   2 approaches
│   │   ├── 03_Sum_of_Naturals.ipynb         #   3 approaches
│   │   ├── 04_Sum_of_Squares_of_Naturals.ipynb  #   3 approaches
│   │   ├── 05_Swap_Two_Numbers.ipynb        #   2 approaches
│   │   ├── 06_Closest_Number.ipynb          #   2 approaches
│   │   ├── 07_Dice_Problem.ipynb            #   2 approaches
│   │   └── 08_Nth_Term_of_AP.ipynb          #   2 approaches
│   │
│   └── 02_Easy_Problems/                    # Easy-level problems
│       ├── 01_Sum_of_Digits.ipynb           #   3 approaches
│       └── 02_Reverse_Digits.ipynb          #   3 approaches
│
├── utils/                                   # Shared tooling
│   ├── complexity_runner.py                 #   AST analyzer + runtime profiler (776 lines)
│   └── __init__.py
│
├── cr.py                                    # One-line loader for the complexity runner
├── assets/                                  # Screenshots & media
├── .gitignore
└── README.md
```

> More sections will be added as practice progresses (Arrays, Strings, Recursion, Sorting, Trees, Graphs, DP, etc.)

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

### 3. Register the Repo Path (one-time setup)

This adds the repo root to your venv's `sys.path` permanently, so `import cr` works from **any subfolder**:

```bash
# Replace the path with your actual repo location
echo "$PWD" > .venv/lib/python3.*/site-packages/dsa-gfg-2026.pth
```

> **This only needs to be done once per venv.** After this, no path manipulation is ever needed in notebooks.

### 4. Open in VS Code or Jupyter

```bash
code .                    # VS Code (recommended)
# or
jupyter notebook          # Classic Jupyter
```

### 5. Run the Setup Cell

Every notebook has a **setup cell** at the top — run it once per session:

```python
# NO_ANALYZE
import cr; import importlib; importlib.reload(cr)
```

That's it. After that, **every cell you run** will automatically display its complexity analysis below the output.

---

## 📓 Notebook Format

Each problem notebook follows a consistent structure:

```
Setup Cell (import cr)
│
├── Problem Statement         — Title, description, examples
│
├── [Approach 1] Naive        — Simple brute-force
│   ├── Explanation (markdown)
│   └── Code + auto complexity panel
│
├── [Approach 2] Alternative  — Improved method (recursion, etc.)
│   ├── Explanation (markdown)
│   └── Code + auto complexity panel
│
└── [Approach 3] Optimal      — Best complexity
    ├── Explanation (markdown)
    └── Code + auto complexity panel
```

---

## 🗂️ Problems Index

### 01 · Logic Building

#### 01 · Basic Problems — 8 problems, 18 approaches

| # | Problem | Approaches | Best Complexity |
|---|---------|-----------|-----------------|
| 01 | **Check Even or Odd** | Modulo (`n % 2`), Bitwise AND (`n & 1`) | O(1) Time · O(1) Space |
| 02 | **Multiplication Table** | Iterative loop, Constant-bounded recursion | O(1) Time · O(1) Space |
| 03 | **Sum of Natural Numbers** | Loop O(n), Recursion O(n), **Formula `n(n+1)/2`** | **O(1) Time · O(1) Space** |
| 04 | **Sum of Squares of Naturals** | Generator O(n), **Formula `n(n+1)(2n+1)/6`**, Overflow-safe variant | **O(1) Time · O(1) Space** |
| 05 | **Swap Two Numbers** | Temp variable, Tuple unpacking (`a, b = b, a`) | O(1) Time · O(1) Space |
| 06 | **Closest Number Divisible by m** | Iterative scan O(m), **Quotient-based formula** | **O(1) Time · O(1) Space** |
| 07 | **Dice Problem (Opposite Face)** | if-else mapping, **Arithmetic (`7 − n`)** | **O(1) Time · O(1) Space** |
| 08 | **Nth Term of AP** | Loop O(n), **Direct formula `a₁ + (n−1)d`** | **O(1) Time · O(1) Space** |

#### 02 · Easy Problems — 2 problems, 6 approaches

| # | Problem | Approaches | Best Complexity |
|---|---------|-----------|-----------------|
| 01 | **Sum of Digits** | Iterative mod/div, Recursion (`n//10`), String conversion (`for c in str(n)`) | **O(log n) Time · O(1) Space** |
| 02 | **Reverse Digits** | Iterative mod/div, Recursion (call-stack unwind), String slicing (`str(n)[::-1]`) | **O(log n) Time · O(1) Space** |

> **Note — Sum of Digits:** No O(1) general solution exists; every digit must be visited, so O(log₁₀n) is the theoretical lower bound. The Digital Root formula (`1 + (n−1) % 9`) runs in O(1) but solves a *different* problem — repeatedly summing digits down to a single digit.

---

### 📊 Progress Summary

| Section | Problems | Approaches | Status |
|---------|----------|-----------|--------|
| 01 · Basic Problems | 8 | 18 | ✅ Complete |
| 02 · Easy Problems | 2 | 6 | ✅ Complete |
| **Total** | **10** | **24** | 🟢 |

---

## 🛠️ Complexity Runner — `utils/complexity_runner.py`

A custom IPython extension (776 lines) that performs **static AST analysis** on every cell execution. Zero external dependencies beyond IPython.

### How It Works

1. **`pre_run_cell`** hook — starts `time.perf_counter()` timer + `tracemalloc`
2. **AST Walk** — parses the cell source code and visits all nodes
3. **Pattern Matching** — detects loops, recursion, built-ins, data structures
4. **`_classify()`** — maps detected patterns to Big-O labels with priority ordering
5. **`post_run_cell`** hook — renders a Catppuccin Mocha-themed HTML panel below the output

### Patterns Detected

#### Time Complexity

| Pattern | Detection Method | Complexity |
|---------|-----------------|------------|
| No loops, no recursion | No loop/call AST nodes | O(1) |
| `range(const, const)` loop | All `range()` args are literals | O(1) |
| Constant-bounded recursion | Counter param with constant default + constant base case | O(1) |
| `for x in str(n)` | `str()` call as loop iterable | O(log n) |
| `str(n)` + `.reverse()` + `.join()` etc. | `str()` detected + implicit iteration builtins | O(log n) |
| `while n > 0: n //= k` or `n >>= k` | `AugAssign(FloorDiv\|RShift)` in while-body | O(log n) |
| `f(n // k)` recursive call | `BinOp(FloorDiv\|RShift)` in recursive call args | O(log n) |
| Binary search (halving loop) | `BinOp(FloorDiv)` in while-body | O(log n) |
| `sum()`, `max()`, `min()`, `any()`, `all()` | Built-in call on non-constant arg | O(n) |
| Single input-scaled loop | `for` / `while` at depth 1 | O(n) |
| Nested loops (depth k) | `for` / `while` at depth k | O(nᵏ) |
| `sort()` / `sorted()` | Attribute or name match | O(n log n) |
| Recursion + loop(s) | Recursion flag + loop depth > 0 | O(n log n) |

#### Space Complexity

| Pattern | Detection Method | Complexity |
|---------|-----------------|------------|
| Scalars only | No data structures, no recursion | O(1) |
| Constant-bounded recursion | Counter param base case | O(1) |
| Generator expression | `GeneratorExp` AST node | O(1) |
| `str(n)` conversion | `str()` call on variable | O(log n) |
| Log-depth recursion (`f(n//k)`) | FloorDiv/RShift in recursive args | O(log n) |
| Linear recursion | Recursion without halving | O(n) |
| List / set / dict comprehension | `ListComp`, `SetComp`, `DictComp` | O(n) |
| Dynamic data structure literals | `list`, `dict`, `set` literals | O(n) |

### Runtime Measurement

| Metric | Method |
|--------|--------|
| Wall-clock time | `time.perf_counter()` (ms precision) |
| Peak memory | `tracemalloc.get_traced_memory()` (KB) |
| `input()` detection | Warns "⚠ includes `input()` wait" when detected |

### Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `show_code=False` | Analysis-only panel | Set `True` for side-by-side code + analysis |
| `# NO_ANALYZE` | — | First line of cell → skip analysis entirely |

### `cr.py` — One-Line Loader

```python
# NO_ANALYZE
import cr; import importlib; importlib.reload(cr)
```

- Forces `sys.modules` cache-busting so edits to `complexity_runner.py` are always picked up
- Uses `_cr_hook` markers for robust hook cleanup across module reloads
- The `.pth` file ensures `cr` is importable from any notebook regardless of subfolder depth

### Known Limitations

| Limitation | Example | Why |
|---|---|---|
| Multi-variable ranges | `range(n - abs(m), n + abs(m))` → shows O(n) instead of O(m) | Requires symbolic range-width evaluation |
| Amortized complexity | `list.append()` is amortized O(1) | AST analysis is static, can't model amortization |
| Hash-based lookups | `dict[key]` or `set.add()` is O(1) avg | Not distinguished from other attribute calls |
| Multi-branch recursion | `fib(n-1) + fib(n-2)` → O(2ⁿ) | Only detects single-path linear recursion |
| Dynamic programming | Memoized recursion → varies | No memo detection yet |

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

Made with ❤️ for consistent DSA practice · **10 problems · 24 approaches** · Updated February 2026

</div>
