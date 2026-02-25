"""
╔══════════════════════════════════════════════════════════════╗
║          DSA Complexity Runner  –  v1.0                      ║
║  Auto-analyzes Time & Space Complexity for every cell run    ║
╚══════════════════════════════════════════════════════════════╝

Setup (add once at the top of your notebook):
    from utils.complexity_runner import setup_complexity_runner
    setup_complexity_runner()

Every cell you run will show:
  • Big-O Time & Space badges (static analysis)
  • Breakdown notes explaining WHY
  • Actual runtime (ms) + peak memory (KB)

To skip analysis on a cell, put as the first line:
    # NO_ANALYZE
"""

import ast
import time
import tracemalloc
import textwrap
from IPython import get_ipython
from IPython.display import display, HTML


# ════════════════════════════════════════════════════════════
#  1.  AST-Based Static Complexity Analyzer
# ════════════════════════════════════════════════════════════

class ComplexityAnalyzer(ast.NodeVisitor):
    """
    Walk a Python AST and detect common Big-O patterns:
      - Loop depth   → O(1) / O(n) / O(n²) / O(n³) …
      - Binary search (halving while-loop) → O(log n)
      - Recursion    → O(n) or O(log n) / O(n log n)
      - sort/sorted  → O(n log n)
      - Dynamic data structures → O(n) space
    """

    def __init__(self):
        self.max_loop_depth    = 0
        self._loop_depth       = 0
        self.has_recursion     = False
        self.has_binary_search = False
        self.has_sort          = False
        self._fn_names         = set()   # functions defined in this snippet
        self._called           = set()   # functions called in this snippet
        self._ds_used          = []      # dynamic data-structure literals
        self.constant_loops    = []      # e.g. ["range(1, 11)"] – fixed-size loops
        self.constant_recursion = False  # True when recursion depth is bounded by a constant
        self.has_binary_search  = False  # kept for backward compat
        self.has_log_loop       = False  # True when while-loop shrinks by division/shift
        self._log_divisor       = 2      # the divisor detected (2, 10, …)
        self.has_log_recursion  = False  # True when recursive call passes n//k or n>>k
        self._log_rec_divisor   = 2      # divisor in the recursive argument
        self.has_str_loop       = False  # True when loop iterates over str(variable)
        self.has_str_conv       = False  # True when str(variable) is called standalone (no loop)
        self.has_implicit_iter  = False  # True when built-in/method iterates (sum, max, .reverse, .join …)
        self.has_sqrt_loop      = False  # True when loop bound involves sqrt(n) or n**0.5

    # ── collect function definitions + true self-recursion ─────

    @staticmethod
    def _has_constant_base_case(func_node: ast.FunctionDef) -> bool:
        """
        Returns True when ALL base-case guards (if <cond>: return) only
        reference parameters that have a *constant* default value — i.e.
        counter params like  i=1  — and NOT the main input variable.

        Example that returns True:
            def printTable(n, i=1):   # i has constant default → counter
                if i > 10: return     # condition uses only 'i' → constant bound
                printTable(n, i+1)

        Example that returns False:
            def factorial(n):
                if n == 0: return 1   # 'n' has no default → main input
                return n * factorial(n-1)
        """
        args     = func_node.args.args
        defaults = func_node.args.defaults

        # Map the LAST len(defaults) params to their default values
        counter_params: set[str] = set()
        if defaults:
            offset = len(args) - len(defaults)
            for idx, default in enumerate(defaults):
                if isinstance(default, ast.Constant):
                    counter_params.add(args[offset + idx].arg)

        if not counter_params:
            return False  # no counter params → can't be constant-bounded

        found_base = False
        for node in ast.walk(func_node):
            if not isinstance(node, ast.If):
                continue
            # Base case = an if-branch whose body is a bare return
            has_bare_return = any(
                isinstance(s, ast.Return) and s.value is None
                for s in node.body
            )
            if not has_bare_return:
                continue
            found_base = True
            # Every Name in the condition must be a counter param
            for name_node in ast.walk(node.test):
                if isinstance(name_node, ast.Name):
                    if name_node.id not in counter_params:
                        return False  # references a non-counter var → unbounded

        return found_base

    @staticmethod
    def _is_log_arg(call_node: ast.Call) -> int | None:
        """
        If any argument of the recursive call is of the form
            n // k   (BinOp FloorDiv)
            n >> k   (BinOp RShift)
        return the divisor k (int), otherwise None.
        """
        for arg in call_node.args:
            if isinstance(arg, ast.BinOp) and isinstance(
                    arg.op, (ast.FloorDiv, ast.RShift)):
                if isinstance(arg.right, ast.Constant) and arg.right.value > 1:
                    divisor = int(arg.right.value)
                    # >> k means divide by 2^k, treat as base-2
                    return 2 if isinstance(arg.op, ast.RShift) else divisor
        return None

    def visit_FunctionDef(self, node):
        self._fn_names.add(node.name)
        # True recursion = function calls itself inside its own body
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if (
                    isinstance(child.func, ast.Name)
                    and child.func.id == node.name
                ):
                    self.has_recursion = True
                    # Constant-bounded recursion (counter param)
                    if self._has_constant_base_case(node):
                        self.constant_recursion = True
                    # Logarithmic recursion: recursive call passes n//k or n>>k
                    divisor = self._is_log_arg(child)
                    if divisor is not None:
                        self.has_log_recursion = True
                        self._log_rec_divisor  = divisor
                    break
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    # ── track function calls ──────────────────────────────────

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            name = node.func.id
            self._called.add(name)
            if name == "sorted":
                self.has_sort = True
            # str(variable) → creates a string of O(log₁₀n) characters
            if (name == "str" and node.args
                    and not all(isinstance(a, ast.Constant) for a in node.args)):
                self.has_str_conv = True
            # Built-in functions that iterate over all elements
            if name in ("sum", "max", "min", "any", "all"):
                if node.args:
                    arg = node.args[0]
                    if not (isinstance(arg, ast.Constant)
                            or self._is_constant_iter(arg)):
                        self.has_implicit_iter = True
            # Constructor calls that allocate + iterate
            if name in ("list", "tuple"):
                if node.args and not all(
                        isinstance(a, ast.Constant) for a in node.args):
                    self.has_implicit_iter = True
        elif isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr in ("sort", "sorted"):
                self.has_sort = True
            # Methods that iterate over the collection
            if attr in ("reverse", "join", "split", "count",
                        "index", "find", "replace"):
                self.has_implicit_iter = True
        self.generic_visit(node)

    # ── for-loops ─────────────────────────────────────────────

    @staticmethod
    def _is_constant_iter(iter_node) -> str | None:
        """
        If iter_node is range() with ALL literal (constant) arguments,
        return a short description string, else return None.
        e.g.  range(10)      → 'range(10)'
              range(1, 11)   → 'range(1, 11)'
              range(n)       → None  (depends on input)
        """
        if not (
            isinstance(iter_node, ast.Call)
            and isinstance(iter_node.func, ast.Name)
            and iter_node.func.id == "range"
        ):
            return None
        if all(isinstance(a, ast.Constant) for a in iter_node.args):
            args_str = ", ".join(str(a.value) for a in iter_node.args)
            return f"range({args_str})"
        return None

    @staticmethod
    def _is_str_iter(iter_node) -> bool:
        """
        Returns True when iter_node is  str(variable)  — i.e. iterating over
        the decimal digits of a number.  The loop runs O(log₁₀n) times, not n.
        e.g.  for ch in str(n)   → True
              for ch in str(42)  → False (constant)
        """
        return (
            isinstance(iter_node, ast.Call)
            and isinstance(iter_node.func, ast.Name)
            and iter_node.func.id == "str"
            and bool(iter_node.args)
            and not all(isinstance(a, ast.Constant) for a in iter_node.args)
        )

    @staticmethod
    def _is_sqrt_range(iter_node) -> bool:
        """
        Returns True when iter_node is  range(..., f(sqrt(n)), ...)  — i.e.
        the loop runs O(\u221an) times.
        Detects:
          range(2, int(math.sqrt(n)) + 1)
          range(2, int(n**0.5) + 1)
          range(int(math.sqrt(n)))
          range(isqrt(n))
          range(2, isqrt(n) + 1)
        """
        if not (
            isinstance(iter_node, ast.Call)
            and isinstance(iter_node.func, ast.Name)
            and iter_node.func.id == "range"
        ):
            return False
        # Walk all range arguments looking for sqrt patterns
        for arg in iter_node.args:
            for node in ast.walk(arg):
                # math.sqrt(x)  or  sqrt(x)
                if isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Attribute) and func.attr == "sqrt":
                        return True
                    if isinstance(func, ast.Name) and func.id in ("sqrt", "isqrt"):
                        return True
                # n ** 0.5  or  n ** (1/2)
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
                    r = node.right
                    if isinstance(r, ast.Constant) and r.value == 0.5:
                        return True
                    # (1/2) as BinOp
                    if (isinstance(r, ast.BinOp) and isinstance(r.op, ast.Div)
                            and isinstance(r.left, ast.Constant) and r.left.value == 1
                            and isinstance(r.right, ast.Constant) and r.right.value == 2):
                        return True
        return False

    def visit_For(self, node):
        const_desc = self._is_constant_iter(node.iter)
        if const_desc:
            # Loop runs a fixed number of times – does NOT scale with input
            self.constant_loops.append(const_desc)
            self.generic_visit(node)   # still visit body for nested analysis
            return
        # str(variable) → iterates over O(log₁₀n) characters, not n
        if self._is_str_iter(node.iter):
            self.has_str_loop  = True
            self.has_log_loop  = True
            self._log_divisor  = 10
            self._loop_depth  += 1
            self.max_loop_depth = max(self.max_loop_depth, self._loop_depth)
            self.generic_visit(node)
            self._loop_depth  -= 1
            return
        # range(..., sqrt(n), ...) → iterates O(√n) times
        if self._is_sqrt_range(node.iter):
            self.has_sqrt_loop = True
            self._loop_depth  += 1
            self.max_loop_depth = max(self.max_loop_depth, self._loop_depth)
            self.generic_visit(node)
            self._loop_depth  -= 1
            return
        self._loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self._loop_depth)
        self.generic_visit(node)
        self._loop_depth -= 1

    # ── while-loops + logarithmic-reduction detection ─────────

    def visit_While(self, node):
        self._loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self._loop_depth)
        # Logarithmic pattern: the loop variable is divided / right-shifted
        # each iteration.  Catches both forms:
        #   n = n // 2      →  Assign(value=BinOp(op=FloorDiv))
        #   n //= 10        →  AugAssign(op=FloorDiv, value=Constant(10))
        #   n >>= 1         →  AugAssign(op=RShift)
        #   mid = (lo+hi)//2 → BinOp inside Assign
        for child in ast.walk(node):
            # AugAssign: n //= k  or  n >>= k
            if isinstance(child, ast.AugAssign) and isinstance(
                    child.op, (ast.FloorDiv, ast.RShift)):
                self.has_log_loop = True
                self.has_binary_search = True
                if isinstance(child.op, ast.RShift):
                    # >>= k means divide by 2^k; treat as base-2
                    self._log_divisor = 2
                elif isinstance(child.value, ast.Constant) and child.value.value != 0:
                    self._log_divisor = int(child.value.value)
                break
            # BinOp inside any expression: n // 2, (lo+hi) // 2
            if isinstance(child, ast.BinOp) and isinstance(
                    child.op, (ast.FloorDiv, ast.RShift)):
                self.has_log_loop = True
                self.has_binary_search = True
                if isinstance(child.right, ast.Constant) and child.right.value != 0:
                    self._log_divisor = int(child.right.value)
                break
        self.generic_visit(node)
        self._loop_depth -= 1

    # ── comprehensions & generator expressions ────────────────
    # These are separate AST nodes (not For), so they need
    # their own visitors. Each generator clause acts like a loop.

    def _process_comprehension(self, generators: list, ds_kind: str | None):
        """
        Shared logic for ListComp, SetComp, DictComp, GeneratorExp.
        Each 'generator' clause (for x in iterable) is one loop level.
        """
        depth = 0
        for gen in generators:
            const_desc = self._is_constant_iter(gen.iter)
            if const_desc:
                self.constant_loops.append(f"{ds_kind or 'genexpr'}:{const_desc}")
            else:
                depth += 1
        if depth > 0:
            self._loop_depth += depth
            self.max_loop_depth = max(self.max_loop_depth, self._loop_depth)
            if ds_kind:
                self._ds_used.append(ds_kind)   # O(n) space for materialised types
            self._loop_depth -= depth

    def visit_ListComp(self, node):
        self._process_comprehension(node.generators, "list")
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self._process_comprehension(node.generators, "set")
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self._process_comprehension(node.generators, "dict")
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        # Generator expressions are lazy — no O(n) space allocation
        self._process_comprehension(node.generators, None)
        self.generic_visit(node)

    # ── data-structure literals ───────────────────────────────

    def visit_List(self, node):
        if node.elts:                        # non-empty list literal
            self._ds_used.append("list")
        self.generic_visit(node)

    def visit_Dict(self, node):
        self._ds_used.append("dict")
        self.generic_visit(node)

    def visit_Set(self, node):
        self._ds_used.append("set")
        self.generic_visit(node)

    # ── main entry point ──────────────────────────────────────

    def analyze(self, code: str) -> dict:
        """Parse *code* and return a complexity dict."""
        try:
            tree = ast.parse(textwrap.dedent(code))
        except SyntaxError as exc:
            return {
                "error": str(exc),
                "time": "?", "space": "?",
                "time_notes": [], "space_notes": [],
            }
        self.visit(tree)
        return self._classify()

    # ── Big-O classification ──────────────────────────────────

    def _classify(self) -> dict:
        tn, sn = [], []          # time-notes, space-notes

        # ── Time Complexity ────────────────────────────────────
        if self.has_recursion and self.constant_recursion:
            # Depth is fixed by a constant counter param – not scaled by n
            tc = "O(1)"
            tn += ["Recursion bounded by a constant counter  \u2192  fixed call depth"]
            tn += ["Recursive calls always run the same number of times"]

        elif self.has_recursion:
            if self.has_log_recursion:
                tc = "O(log n)"
                base = self._log_rec_divisor
                if base == 2:
                    tn += ["Recursive call passes n//2 (or n>>k)  \u2192  O(log\u2082n) depth"]
                elif base == 10:
                    tn += ["Recursive call passes n//10  \u2192  O(log\u2081\u2080n) depth"]
                else:
                    tn += [f"Recursive call passes n//{base}  \u2192  O(log n) depth"]
            elif self.has_binary_search:
                tc = "O(log n)"
                tn += ["Recursive halving \u2192 divide & conquer"]
            elif self.max_loop_depth == 0:
                tc = "O(n)"
                tn += ["Linear recursion (single path, no branching)"]
            else:
                tc = "O(n log n)"
                tn += [f"Recursion  +  {self.max_loop_depth} loop level(s)"]

        elif self.has_sort:
            tc = "O(n log n)"
            tn += ["Built-in sort / sorted  →  O(n log n)"]
            if self.max_loop_depth >= 1:
                tn += [f"Sort called inside {self.max_loop_depth} loop(s)"]

        elif self.max_loop_depth == 0:
            if self.has_str_conv:
                tc = "O(log n)"
                tn += ["str(n) operates on O(log\u2081\u2080n) digits  \u2192  O(log\u2081\u2080n) time"]
                if self.has_implicit_iter:
                    tn += ["Built-in calls (.reverse, .join, list\u2026) also operate on digit-length data"]
            elif self.has_implicit_iter:
                tc = "O(n)"
                tn += ["Built-in operations iterate over input  \u2192  linear time"]
            elif self.constant_loops:
                tc = "O(1)"
                descs = ", ".join(self.constant_loops)
                tn += [f"Loop(s) over fixed range ({descs})  \u2192  constant time"]
            else:
                tc = "O(1)"
                tn += ["No loops or recursion  →  constant time"]

        elif self.max_loop_depth == 1:
            if self.has_sqrt_loop:
                tc = "O(\u221an)"
                tn += ["Loop runs up to \u221an iterations (sqrt-bounded range)"]
            elif self.has_log_loop:
                tc = "O(log n)"
                if self.has_str_loop:
                    tn += ["Loop iterates over str(n)  →  O(log\u2081\u2080n) digits"]
                else:
                    base = self._log_divisor
                    if base == 2:
                        tn += ["Loop halves the input each iteration  →  O(log\u2082n)"]
                    elif base == 10:
                        tn += ["Loop divides input by 10 each iteration  →  O(log\u2081\u2080n)"]
                    else:
                        tn += [f"Loop divides input by {base} each iteration  →  O(log n)"]
            else:
                tc = "O(n)"
                tn += ["Single loop  →  linear time"]

        elif self.max_loop_depth == 2:
            tc = "O(n²)"
            tn += ["2 nested loops  →  quadratic time"]

        elif self.max_loop_depth == 3:
            tc = "O(n³)"
            tn += ["3 nested loops  →  cubic time"]

        else:
            tc = f"O(n^{self.max_loop_depth})"
            tn += [f"{self.max_loop_depth} nested loops  →  polynomial time"]

        # Extra context notes
        if self.has_recursion and not self.constant_recursion:
            tn += ["Recursive function call(s) present"]
        if self.has_sort:
            tn += ["Sorting operation detected"]

        # ── Space Complexity ───────────────────────────────────
        if self.has_recursion and self.constant_recursion:
            sc = "O(1)"
            sn += ["Call stack depth is fixed by a constant  \u2192  constant space"]
        elif self.has_recursion and self.has_log_recursion:
            sc = "O(log n)"
            base = self._log_rec_divisor
            label = f"log\u2081\u2080n" if base == 10 else (f"log\u2082n" if base == 2 else "log n")
            sn += [f"Recursive call stack shrinks by factor {base}  \u2192  O({label}) depth"]
        elif self.has_recursion:
            sc = "O(n)"
            sn += ["Recursive call stack  →  O(n) depth"]
        elif self._ds_used:
            sc = "O(n)"
            ds_str = ", ".join(sorted(set(self._ds_used)))
            sn += [f"Dynamic structure(s) allocated: {ds_str}"]
        elif self.has_str_loop or self.has_str_conv:
            sc = "O(log n)"
            sn += ["str(n) allocates O(log\u2081\u2080n) characters  \u2192  O(log n) space"]
        else:
            sc = "O(1)"
            sn += ["Only scalar / fixed-size variables  →  constant space"]

        return dict(
            time=tc, space=sc,
            time_notes=tn, space_notes=sn,
            loop_depth=self.max_loop_depth,
            has_recursion=self.has_recursion,
            has_sort=self.has_sort,
            has_binary_search=self.has_binary_search,
        )


# ════════════════════════════════════════════════════════════
#  2.  Color Palette  (Catppuccin Mocha-inspired)
# ════════════════════════════════════════════════════════════

_PALETTE = {
    "O(1)":       ("#22c55e", "#052e16"),   # green  – best
    "O(log n)":   ("#84cc16", "#1a2e05"),   # lime
    "O(\u221an)":     ("#06b6d4", "#083344"),   # cyan   – sqrt
    "O(n)":       ("#3b82f6", "#0c1a3d"),   # blue
    "O(n log n)": ("#f59e0b", "#3d2200"),   # amber
    "O(n\u221an)":    ("#e879f9", "#3b0764"),   # fuchsia
    "O(n²)":      ("#f97316", "#3d1500"),   # orange
    "O(n³)":      ("#ef4444", "#3d0c0c"),   # red    – worst common
}


def _badge_colors(label: str):
    return _PALETTE.get(label, ("#a855f7", "#2d0b4e"))   # purple for exotic


def _esc(s: str) -> str:
    """Minimal HTML escape."""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


# ════════════════════════════════════════════════════════════
#  3.  HTML Builder  –  side-by-side panel
# ════════════════════════════════════════════════════════════

_CSS = """
<style>
  .cr-wrap {
    display: flex; gap: 0;
    font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px;
    border: 1px solid #313244; border-radius: 10px;
    overflow: hidden; margin: 8px 0;
    box-shadow: 0 4px 12px rgba(0,0,0,.5);
  }
  /* ── Left panel (code) ── */
  .cr-left {
    flex: 1.5; border-right: 1px solid #313244;
    padding: 12px 14px; background: #11111b;
  }
  /* ── Right panel (analysis) ── */
  .cr-right {
    flex: 1; padding: 12px 14px;
    background: #1e1e2e; color: #cdd6f4;
    min-width: 240px;
  }
  /* ── Shared section label ── */
  .cr-section {
    font-size: 10px; font-weight: 700;
    letter-spacing: .08em; color: #585b70;
    margin: 6px 0 4px; text-transform: uppercase;
  }
  /* ── Code block ── */
  .cr-code {
    background: #181825; border-radius: 6px;
    padding: 10px 12px;
    font-family: 'Fira Code','Cascadia Code','Courier New',monospace;
    font-size: 12.5px; white-space: pre; overflow-x: auto;
    color: #cdd6f4; line-height: 1.65; margin: 0;
    border: 1px solid #313244;
  }
  /* ── Badge row ── */
  .cr-badges { display: flex; gap: 8px; margin: 6px 0 10px; }
  .cr-badge {
    flex: 1; border: 2px solid; border-radius: 8px;
    padding: 8px 6px; text-align: center;
  }
  .cr-badge-label {
    font-size: 10px; font-weight: 700;
    letter-spacing: .06em; margin-bottom: 3px;
  }
  .cr-badge-val {
    font-size: 17px; font-weight: 800;
    font-family: 'Fira Code', monospace;
  }
  /* ── Breakdown notes ── */
  .cr-note { font-size: 12px; color: #a6adc8; padding: 2px 0 2px 2px; }
  .cr-note-t::before { content: "⏱ "; }
  .cr-note-s::before { content: "💾 "; }
  .cr-dim { color: #45475a; }
  /* ── Performance table ── */
  .cr-perf { border-collapse: collapse; width: 100%; margin-top: 4px; }
  .cr-plabel { color: #585b70; font-size: 12px; padding: 3px 8px 3px 0; width: 105px; }
  .cr-pval   { font-weight: 700; font-size: 13px; color: #cdd6f4; }
  .cr-warn   { font-size: 11px; color: #f38ba8; padding-left: 6px; }
  .cr-error  { color: #f38ba8; }
  /* ── Divider ── */
  .cr-hr { border: none; border-top: 1px solid #313244; margin: 8px 0; }
</style>
"""


def build_complexity_html(
    code: str,
    analysis: dict,
    runtime_ms: float,
    peak_kb: float,
    has_input: bool = False,
    show_code: bool = False,
) -> str:
    """Return a full HTML string with optional code panel on the left and analysis on the right."""

    tc  = analysis.get("time",  "?")
    sc  = analysis.get("space", "?")
    tn  = analysis.get("time_notes",  [])
    sn  = analysis.get("space_notes", [])
    err = analysis.get("error")

    tc_fg, tc_bg = _badge_colors(tc)
    sc_fg, sc_bg = _badge_colors(sc)

    code_html = _esc(code.strip())

    # ── Breakdown notes ──
    notes_html = ""
    for n in tn:
        notes_html += f'<div class="cr-note cr-note-t">{_esc(n)}</div>'
    for n in sn:
        notes_html += f'<div class="cr-note cr-note-s">{_esc(n)}</div>'
    if not notes_html:
        notes_html = '<div class="cr-note cr-dim">No special patterns detected.</div>'

    # ── Right-panel content ──
    if err:
        right_body = f'<div class="cr-error">❌ Parse error: {_esc(err)}</div>'
    else:
        warn_td = (
            f'<td class="cr-warn">⚠ includes input() wait</td>'
            if has_input else "<td></td>"
        )
        right_body = f"""
        <div class="cr-section">Complexity</div>
        <div class="cr-badges">
          <div class="cr-badge"
               style="color:{tc_fg};background:{tc_bg};border-color:{tc_fg}">
            <div class="cr-badge-label">⏱ TIME</div>
            <div class="cr-badge-val">{_esc(tc)}</div>
          </div>
          <div class="cr-badge"
               style="color:{sc_fg};background:{sc_bg};border-color:{sc_fg}">
            <div class="cr-badge-label">💾 SPACE</div>
            <div class="cr-badge-val">{_esc(sc)}</div>
          </div>
        </div>

        <div class="cr-section">Breakdown</div>
        {notes_html}

        <hr class="cr-hr"/>
        <div class="cr-section">Actual Performance</div>
        <table class="cr-perf">
          <tr>
            <td class="cr-plabel">Runtime</td>
            <td class="cr-pval">{runtime_ms:.3f} ms</td>
            {warn_td}
          </tr>
          <tr>
            <td class="cr-plabel">Peak Memory</td>
            <td class="cr-pval">{peak_kb:.2f} KB</td>
            <td></td>
          </tr>
        </table>
        """

    left_panel = ""
    if show_code:
        left_panel = f"""
  <div class="cr-left">
    <div class="cr-section">Code</div>
    <pre class="cr-code">{code_html}</pre>
  </div>"""

    return f"""
{_CSS}
<div class="cr-wrap">
  {left_panel}
  <div class="cr-right" style="{'border-radius:10px' if not show_code else ''}">
    {right_body}
  </div>
</div>
"""


# ════════════════════════════════════════════════════════════
#  4.  IPython Event Hooks  –  auto-analyze every cell
# ════════════════════════════════════════════════════════════

_state: dict = {}   # shared state between pre/post hooks


def _pre_run(info):
    """Called just BEFORE a cell executes — start the clock & tracer."""
    src = info.raw_cell or ""
    skip = (
        not src.strip()
        or src.lstrip().startswith("# NO_ANALYZE")
        or "complexity_runner"      in src
        or "setup_complexity_runner" in src
        or src.lstrip().startswith(("%", "!", "?"))
    )
    _state.update(src=src, skip=skip, t0=0.0)
    if not skip:
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        tracemalloc.start()
        _state["t0"] = time.perf_counter()


def _post_run(_result):
    """Called just AFTER a cell executes — display the analysis panel."""
    if _state.get("skip"):
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        return

    elapsed_ms = (time.perf_counter() - _state.get("t0", time.perf_counter())) * 1000

    if tracemalloc.is_tracing():
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_kb = peak / 1024
    else:
        peak_kb = 0.0

    src = _state.get("src", "").strip()
    if not src:
        return

    has_input = "input(" in src
    analysis  = ComplexityAnalyzer().analyze(src)
    html      = build_complexity_html(
        src, analysis, elapsed_ms, peak_kb, has_input,
        show_code=_state.get("show_code", False),
    )
    display(HTML(html))


# ════════════════════════════════════════════════════════════
#  5.  Public API
# ════════════════════════════════════════════════════════════

def setup_complexity_runner(show_code: bool = False) -> None:
    """
    Register the auto-analyze hooks on the current IPython kernel.
    Call this ONCE at the top of your notebook.

    Parameters
    ----------
    show_code : bool
        If True, display the cell's source code alongside the analysis panel.
        Default is False (analysis panel only).
    """
    ip = get_ipython()
    if ip is None:
        print("⚠  Not running inside IPython/Jupyter – nothing registered.")
        return

    _state["show_code"] = show_code

    # ── Remove ALL previously registered CR hooks ──────────────
    # Handles module reloads where old function references differ
    for event_name in ("pre_run_cell", "post_run_cell"):
        old_cbs = [cb for cb in ip.events.callbacks.get(event_name, [])
                   if getattr(cb, '_cr_hook', False)]
        for cb in old_cbs:
            try:
                ip.events.unregister(event_name, cb)
            except ValueError:
                pass

    # ── Mark and register fresh hooks ──────────────────────────
    _pre_run._cr_hook  = True
    _post_run._cr_hook = True
    ip.events.register("pre_run_cell",  _pre_run)
    ip.events.register("post_run_cell", _post_run)

    code_mode = "with code" if show_code else "analysis only (no code panel)"
    print("✅  Complexity Runner is now active!")
    print(f"    ├─ Mode: {code_mode}")
    print("    ├─ Every cell will show Time & Space complexity after it runs.")
    print("    └─ Add  # NO_ANALYZE  as the first line of any cell to skip it.\n")


def teardown_complexity_runner() -> None:
    """Remove the complexity-analysis hooks (disable auto-analyze)."""
    ip = get_ipython()
    if ip:
        for event_name in ("pre_run_cell", "post_run_cell"):
            old_cbs = [cb for cb in ip.events.callbacks.get(event_name, [])
                       if getattr(cb, '_cr_hook', False)]
            for cb in old_cbs:
                try:
                    ip.events.unregister(event_name, cb)
                except ValueError:
                    pass
    print("Complexity Runner disabled.")
