# Issues Identified and Resolved — Lab 5: Static Code Analysis

## Summary of Analysis Tools
- **Pylint**: Evaluated code quality, adherence to Python standards, docstrings, variable naming, scope, and potential anti-patterns.
- **Bandit**: Scanned for potential security vulnerabilities including code injection, insecure random number generation, and silent exception handling.
- **Flake8**: Checked for PEP 8 styling, line lengths, unused imports/variables, and whitespace conventions.

---

## Issue Tracking Table

| Issue | Tool | Type / Severity | Line(s) | Description | Fix Approach |
|---|---|---|---|---|---|
| **Arbitrary Code Execution via `eval`** | Bandit & Pylint | Security / Medium (B307, W0123) | 27 | Using `eval(code_str)` to evaluate user-supplied promo code strings allows execution of arbitrary code or OS commands. | Replaced `eval` with a secure abstract syntax tree (`ast`) parser (`ast.parse` in `eval` mode) evaluating only whitelisted safe arithmetic operators (`+`, `-`, `*`, `/`). |
| **Insecure Pseudo-Random Generator** | Bandit | Security / Low (B311) | 21 | `random.randint(1000, 9999)` relies on standard PRNG unsuitable for unpredictable token/receipt generation. | Replaced `random.randint` with the cryptographically secure `secrets.randbelow(9000) + 1000`. |
| **Silent Exception Swallowing (`try-except-pass`)** | Bandit & Pylint | Bug / Security / Low (B110, W0718) | 33-34 | A catch-all `except Exception: pass` silently masks runtime failures and catalog bugs during stock update. | Replaced broad exception catching with explicit dictionary membership checking (`if item in PRICE_LIST`) and descriptive feedback. |
| **Dangerous Mutable Default Argument** | Pylint | Bug / Code Quality (W0102) | 10 | `receipts=[]` as a default argument persists and mutates across subsequent function calls. | Changed default parameter to `receipts: Optional[List[float]] = None` and initialized `if receipts is None: receipts = []` inside the method. |
| **Bare `except:` Catching System Interrupts** | Pylint & Flake8 | Bug / Style (W0702, E722) | 16 | Bare `except:` catches `KeyboardInterrupt`, `SystemExit`, and hides all unexpected syntax or system errors. | Replaced bare except with explicit handling of `(ValueError, TypeError)` and catalog existence validation. |
| **Unclosed File Handle & Missing Encoding** | Pylint | Resource / Reliability (R1732, W1514) | 37 | File opened with `f = open(file, "a")` without explicit UTF-8 encoding or proper context manager closure, risking file handle leakage. | Refactored file I/O to use `with open(file_path, "a", encoding="utf-8") as file:`. |
| **Global State Mutation** | Pylint | Architecture / Maintainability (W0603, C0103) | 7, 11 | `global sales_total` and module-level variables create hard-to-test global mutable state. | Refactored POS state into an encapsulated `POSSystem` class with instance attributes `sales_total` and `receipt_lines`. |
| **Unused Imports and Dead Variables** | Flake8 & Pylint | Style / Cleanliness (F401, F841, W0611, W0612) | 1, 3, 26 | `import json` and `import logging` were unused; `total = sales_total` in `apply_promo_code` was assigned and never used. | Removed unused imports and cleaned up redundant variable assignments. |
| **PEP 8 Formatting, Docstrings & Naming Violations** | Flake8 & Pylint | Style / Standards (E302, E305, E501, C0114, C0116, C0103) | 1, 10, 21, 41 | Missing module and function docstrings, line lengths exceeding 79 chars, non-snake_case function names (`printSales`). | Added comprehensive docstrings, wrapped long lines to under 79 characters, and adhered to PEP 8 naming conventions. |

---

## Verification Results Summary

- **Pylint Score**:
  - *Before*: **5.65 / 10**
  - *After*: **10.00 / 10** (Target > 9.5 achieved)
- **Bandit Findings**:
  - *Before*: 3 issues (1 Medium severity CWE-78, 2 Low severity CWE-330 / CWE-703)
  - *After*: **0 issues**
- **Flake8 Violations**:
  - *Before*: 12 PEP 8 violations
  - *After*: **0 violations (Clean)**
