# Evaluating the Best Python Type Checkers (2026)

*A cited evaluation of mypy, Pyright, ty (Astral), Pyrefly (Meta), Pyre, and
pytype — compared on speed, conformance, IDE integration, ergonomics,
adoption, and maturity, with recommendations by use case.*

**Last updated:** June 2026 · **Status:** point-in-time snapshot — versions,
benchmarks, and conformance scores move fast; re-check before relying on a
specific number.

---

## TL;DR

| Checker | Maker | Language | Status (2026) | Speed | Spec conformance¹ | Best for |
|---|---|---|---|---|---|---|
| **Pyright** | Microsoft | TypeScript | Mature, active | Fast (~3–5× mypy) | **Highest (~90%+)** | IDE use, libraries, correctness |
| **mypy** | python org | Python | Mature, reference | Slowest (use `dmypy`) | Mid (~65%) | Incumbent CI, plugin ecosystem |
| **Pyrefly** | Meta | Rust | **Stable 1.0 (May 2026)** | Very fast (10–50×) | High (~85–90%) | Large monorepos, app teams |
| **ty** | Astral | Rust | **Beta (Dec 2025)** | Fastest, esp. incremental | Lower (~75%), rising | Editor feedback, early adopters |
| **Pyre** | Meta | OCaml | Maintenance (superseded) | n/a | not listed | — (migrate to Pyrefly) |
| **pytype** | Google | Python | **Sunset (Aug 2025)** | Slow | not listed | — (migrate off) |

¹ Conformance = pass rate on the official [`python/typing` conformance
suite](https://github.com/python/typing/blob/main/conformance/README.md)
(~139 tests). Scores are **version-dependent and drift between releases** —
see [Standards & Conformance](#5-standards--conformance).

**Bottom line:** For most teams in 2026, **Pyright** (via Pylance) remains the
safest default for correctness and IDE experience, and **mypy** is fine if
you're already invested in it. The Rust-based newcomers have changed the
landscape: **Pyrefly** is now production-ready (stable 1.0) and excellent for
large codebases, while **ty** is the fastest for editor feedback but still in
beta. The two legacy checkers, **Pyre** and **pytype**, are both winding down.

---

## 1. The 2026 landscape

Two things define the Python type-checking landscape this year:

1. **A generational shift to Rust.** Both Meta and Astral shipped new
   Rust-based checkers built around *incremental* analysis and *LSP-native*
   language-server design. They are an order of magnitude faster than the
   incumbents and are reshaping expectations.
2. **The old guard is consolidating.** Google's **pytype** entered bugfix-only
   maintenance in August 2025, and Meta's **Pyre** is being superseded by its
   own successor, **Pyrefly**. That leaves four checkers worth actively
   considering: **mypy, Pyright, Pyrefly, and ty.**

Adoption signals (from the JetBrains/Meta/Microsoft *Typed Python* surveys):

- **2024 survey** (~1,000+ respondents): 88% "Always/Often" use type hints;
  **mypy 67%, Pyright 38%**, ~24% use both.
  ([Engineering at Meta, Dec 2024](https://engineering.fb.com/2024/12/09/developer-tools/typed-python-2024-survey-meta/))
- **2025 survey** (1,241 respondents): **mypy 58%** (down from ~61%),
  **Pyright/Pylance** second, and the new Rust checkers (**Pyrefly, ty,
  Zuban**) collectively used by **>20%** already.
  ([Engineering at Meta, Dec 2025](https://engineering.fb.com/2025/12/22/developer-tools/python-typing-survey-2025-code-quality-flexibility-typing-adoption/))

> ⚠️ These are typing-engaged, self-selected audiences, and the two waves used
> slightly different framing, so the mypy 67%→58% "drop" is **partly
> methodological**, not a clean year-over-year comparison.

---

## 2. The checkers at a glance

### mypy — the incumbent reference
- Launched **2012**; lives under [`python/mypy`](https://github.com/python/mypy).
  Often called the "reference implementation," though
  [PEP 729](https://peps.python.org/pep-0729/) does **not** formally confer
  that title.
- **By default skips unannotated functions** (unless `--check-untyped-defs` /
  `--strict`) and **never infers return types** — an unannotated function is
  treated as returning `Any`.
  ([Pyright's mypy-comparison.md](https://github.com/microsoft/pyright/blob/main/docs/mypy-comparison.md))
- Slowest of the group, but the **`dmypy` daemon** keeps state in memory for
  incremental runs "often a few hundred ms" and "10 or more times faster" than
  the CLI.
  ([mypy daemon docs](https://mypy.readthedocs.io/en/stable/mypy_daemon.html))
- **Mature plugin ecosystem** (Django, SQLAlchemy, etc.) — though mypy's docs
  caution the plugin API is not officially supported for third-party use.
- **No built-in language server**; editor integration relies on third-party
  plugins.

### Pyright — the IDE powerhouse
- From **Microsoft**, first released ~2019, written in **TypeScript** on
  Node.js. Latest: **v1.1.410 (May 23, 2026)**.
  ([microsoft/pyright](https://github.com/microsoft/pyright))
- **Pyright is the engine; [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
  is Microsoft's VS Code extension that wraps it** — giving most Python
  developers first-class, zero-config language services (autocomplete, hover,
  go-to-def, rename, auto-imports).
- **Checks all code by default, including unannotated functions, and infers
  return types.** Uses lazy/JIT evaluation and its own error-recovering parser
  — designed from day one as a language-server foundation.
- **Four modes:** `off`, `basic`, `standard` (default), `strict`.
  ([configuration.md](https://github.com/microsoft/pyright/blob/main/docs/configuration.md))

### Pyrefly — Meta's Rust successor to Pyre
- **Stable [v1.0.0 released May 12, 2026](https://github.com/facebook/pyrefly/releases/tag/1.0.0)**,
  explicitly "production ready." Timeline: alpha (May 2025, PyCon US) → beta
  (Nov 2025) → stable (May 2026).
- **From-scratch Rust rewrite of Pyre** (which was OCaml); motivated by
  cross-platform support and growing the contributor community.
  ([Lessons from Pyre](https://pyrefly.org/blog/lessons-from-pyre))
- **Aggressive inference**: infers types in most positions *including return
  types of unannotated functions*, so it catches errors in untyped/legacy code
  that mypy skips by default (configurable via `untyped-def-behavior`).
- **Migration tooling**: `pyrefly init` auto-migrates mypy/pyright configs;
  config **presets** (`off`/`basic`/`legacy`/`default`/`strict`); built-in
  Pydantic & Django modeling; Jupyter `.ipynb` at full parity with `.py`.
- **Default checker for Instagram's ~20M-line codebase**; also adopted by
  **PyTorch and JAX**. MIT licensed.

### ty — Astral's incremental speed demon
- **Beta, announced [Dec 16, 2025](https://astral.sh/blog/ty)**; versioned
  `0.0.x` with **no stable API yet** (a 1.0 is targeted for 2026). Astral says
  it uses ty internally and recommends it "for motivated users for production
  use."
- From **Astral** (makers of **Ruff** and **uv**), written in **Rust**,
  developed inside the Ruff repo (formerly "red-knot"). Run via `uvx ty check`.
- **Architected around incrementality** to power a language server — its
  standout result is editor responsiveness (see below). Features first-class
  intersection types, sophisticated reachability analysis, advanced narrowing.
- Follows the **gradual guarantee**: adding annotations to working code should
  never introduce new errors.

### Pyre & pytype — winding down
- **Pyre (Meta):** in maintenance, superseded by Pyrefly. README now points
  users to Pyrefly; last release **0.9.25 (Jul 7, 2025)**. Not archived, but no
  longer the active investment.
  ([facebook/pyre-check](https://github.com/facebook/pyre-check),
  [PyPI](https://pypi.org/project/pyre-check/))
- **pytype (Google):** **bugfix-only since [Aug 20, 2025](https://github.com/google/pytype/issues/1925)**;
  Python **3.12 is the last supported version**. Its distinctive
  bytecode-based *inference without annotations* couldn't keep pace with new
  typing PEPs and LSP needs. Google now points users to mypy/Pyright/Pyrefly/ty.

---

## 3. Performance & speed

The headline story of 2026: the Rust checkers are roughly an **order of
magnitude** faster than mypy and Pyright, and the gap widens on large
codebases and in incremental/editor scenarios.

**Why:** mypy is Python; Pyright is TypeScript/Node; **ty and Pyrefly are
Rust** with architectures built around fine-grained incremental recomputation.
That's what enables per-keystroke checking.

### Full-check benchmarks (cold, no cache)

| Codebase | mypy | Pyright | Pyrefly | ty |
|---|---|---|---|---|
| **PyTorch** | 48.1 s | 35.2 s | **2.4 s** | — |
| **Home Assistant** (~1M LOC) | ~45.7 s | ~19.6 s | ~4.8 s | **~2.2 s** |
| **pandas** | — | 144 s | 1.9 s | **1.5 s** |
| **numpy** | — | 70.9 s (>3 GB RAM) | **4.8 s** (1 GB) | ~30.6 s* |

*Sources: [Meta's Pyrefly launch (PyTorch/Instagram)](https://engineering.fb.com/2025/05/15/developer-tools/introducing-pyrefly-a-new-type-checker-and-ide-experience-for-python/),
[Pyrefly speed & memory comparison](https://pyrefly.org/blog/speed-and-memory-comparison/),
[Astral ty beta](https://astral.sh/blog/ty). \*numpy is a known
pathological case for ty (overload-heavy numeric code) — flagged as an
outlier.*

- Vendor headline multipliers: **Pyright ~3–5× mypy**; **Pyrefly ~10–50×** mypy
  and Pyright; **ty "10×–100×"** (also stated as "10–60×" / "80× faster than
  Pyright" depending on baseline and version). Don't cite a single universal
  multiplier.
- Pyrefly checks **>1.85 million lines/sec** and rechecks in IDEs in **<10 ms**
  after save. ([v1.0 notes](https://github.com/facebook/pyrefly/releases/tag/1.0.0))

### Incremental / editor responsiveness (ty's strongest result)

Editing a load-bearing file in **PyTorch** and recomputing diagnostics:

- **ty: ~4.7 ms**
- **Pyright: ~386 ms** (~80× slower)
- **Pyrefly: ~2.38 s** (~500× slower)

([Astral, Dec 2025](https://astral.sh/blog/ty); corroborated by
[Simon Willison](https://simonwillison.net/2025/Dec/16/ty/))

### Memory

ty and Pyrefly use far less memory than Pyright/mypy on large projects (e.g.
numpy: Pyright >3 GB vs Pyrefly ~1 GB). In the **ty-vs-Pyrefly** matchup,
**ty wins on incremental latency**, while **Pyrefly tends to win on memory
footprint** (Pyrefly reports 40–60% less memory than at its own beta).

> ⚠️ Most of these numbers are **vendor-authored benchmarks**, repeated by
> third parties but not always independently reproduced. The most neutral
> cross-checks (e.g. [Edward Li's comparison](https://blog.edward-li.com/tech/comparing-pyrefly-vs-ty/),
> [Posit/Positron](https://opensource.posit.co/blog/2026-03-31_python-type-checkers/))
> broadly confirm the order-of-magnitude gaps.

---

## 4. IDE integration & ergonomics

| Checker | Language server | Editor story |
|---|---|---|
| **Pyright** | ✅ (purpose-built) | **Best-in-class** via Pylance in VS Code/Cursor; zero config. The default most devs already have. |
| **Pyrefly** | ✅ full LSP | VS Code, Neovim, Zed, and **native in PyCharm 2026.1.2+**. Safe Delete, bulk fixes, rich hovers. |
| **ty** | ✅ (incremental-first) | Official VS Code/Cursor extension; **ships in Zed** out of the box; **PyCharm 2025.3+** native support. Playground at play.ty.dev. |
| **mypy** | ❌ none built-in | Relies on third-party plugins / IDE-specific integrations. |

Ergonomics notes:
- **mypy** is lenient by default (skips untyped code) — gentle for gradual
  adoption but misses errors unless you opt into `--strict`.
- **Pyright/Pyrefly/ty** check everything by default and infer more, surfacing
  more issues out of the box (which can mean more false positives early on).
- **Pyrefly and ty** both ship first-class **config migration** from
  mypy/pyright and **preset** severity bundles, lowering switching cost.

---

## 5. Standards & conformance

Conformance = pass rate on the official **[`python/typing` conformance
suite](https://github.com/python/typing/blob/main/conformance/README.md)**
(~139 tests), maintained by the **Typing Council** established in
[PEP 729](https://peps.python.org/pep-0729/) (members include Eric Traut of
Pyright, Guido van Rossum, Jelle Zijlstra, Rebecca Chen of pytype, Shantanu
Jain).

**Live results, mid-2026** ([results.html](https://github.com/python/typing/blob/main/conformance/results/results.html)):

| Checker (version) | Conformance |
|---|---|
| **Pyright (1.1.409)** | **~90%** (highest) |
| Zuban (0.7.2) | ~88% |
| Pyrefly (1.0.0) | ~85% |
| pycroscope (0.4.0) | ~78% |
| ty (0.0.40) | ~75% |
| mypy (2.1.0) | ~65% |

> ⚠️ **These numbers drift between releases and snapshots.** Earlier-2026 blog
> snapshots reported Pyright ~98% / mypy ~57–58% / ty ~15–53% — different dates,
> versions, and sub-metrics. What's **robust**: Pyright leads, mypy sits
> mid-pack, Pyrefly is high and climbing, ty is lower but rising fast (its low
> score reflects *deliberately unimplemented* features being filled in, not a
> broken type system). Pyre and pytype are no longer listed.

**Practical implication:** because mypy and Pyright genuinely disagree on edge
cases (ParamSpec, recursive types, complex overloads, TypeVarTuple, type
guards), **library authors should test against more than one checker** and ship
a `py.typed` marker per [PEP 561](https://peps.python.org/pep-0561/) so
downstream users of either tool get correct results.

The conformance page itself cautions **against** picking a checker on score
alone — the suite stresses advanced edge cases most codebases never hit.

---

## 6. Known limitations

- **ty (beta):** no plugin system yet (can't replace mypy where Django/Pydantic
  plugins are needed); higher memory use; real-world false positives (in one
  eval against `pydantic-ai`, 337/417 diagnostics were false positives —
  [#3970](https://github.com/pydantic/pydantic-ai/issues/3970)); `0.0.x` API
  churn; stricter dynamic-attribute handling.
- **Pyrefly:** not semver-stable (minor releases may introduce new type
  errors); ~10–15% of spec edge cases still unmet; tensor-shape checking and
  baseline files are experimental.
- **mypy:** slow without `dmypy`; lenient defaults; mid-pack conformance; no
  native LSP.
- **Pyright:** TypeScript/Node runtime (not Rust-fast on huge repos);
  CLI-as-CI is solid but Pylance's richest features are VS Code-bound.
- **Pyre / pytype:** winding down — not recommended for new projects.

---

## 7. Recommendations by use case

### Large monorepos (millions of LOC)
**→ Pyrefly** (stable, proven on Instagram/PyTorch/JAX, fast full checks, low
memory) or **ty** if editor latency is the priority and you can tolerate beta.
mypy only with `dmypy` and fine-grained incremental config.

### Library authors (publishing typed packages)
**→ Pyright as primary, plus mypy in CI** — test against both for the widest
downstream correctness, ship `py.typed`. Pyright's high conformance catches the
spec edge cases your users' checkers will hit.

### Application teams (web apps, services)
**→ Pyright/Pylance** for the default IDE+CI experience, **or Pyrefly** if you
want one fast Rust tool for both IDE and CI with easy mypy/pyright config
migration and good Django/Pydantic support.

### Editor / inner-loop feedback
**→ ty** (unmatched incremental recompute, ~4.7 ms) or **Pyright via Pylance**
(maturity + ecosystem). Both give near-instant per-keystroke feedback.

### CI pipelines
**→ Pyright** (mature, deterministic CLI, highest conformance) or **mypy** if
already embedded. **Pyrefly** is a strong, much faster CI option now that it's
1.0. Pin the version — conformance and diagnostics shift between releases.

### Migrating off Pyre or pytype
**→ Pyrefly** (natural successor to Pyre, with migration tooling) or
**Pyright/mypy**. pytype users should plan a move now that it's bugfix-only and
capped at Python 3.12.

---

## 8. The one-line verdict

> **Pyright** is the safest all-around default in 2026 (correctness + IDE).
> **Pyrefly** is the best new Rust checker for production codebases today.
> **ty** is the fastest for editor feedback but still beta. **mypy** remains a
> fine incumbent. **Pyre** and **pytype** are end-of-the-road — migrate off.

---

## Sources

**Primary (directly verified):**
- [github.com/facebook/pyrefly](https://github.com/facebook/pyrefly) ·
  [v1.0.0 release](https://github.com/facebook/pyrefly/releases/tag/1.0.0) ·
  [v0.42.0 beta](https://github.com/facebook/pyrefly/releases/tag/0.42.0)
- [github.com/astral-sh/ty](https://github.com/astral-sh/ty) ·
  [releases](https://github.com/astral-sh/ty/releases)
- [github.com/microsoft/pyright](https://github.com/microsoft/pyright) ·
  [mypy-comparison.md](https://github.com/microsoft/pyright/blob/main/docs/mypy-comparison.md) ·
  [configuration.md](https://github.com/microsoft/pyright/blob/main/docs/configuration.md)
- [github.com/python/mypy](https://github.com/python/mypy) ·
  [mypy daemon docs](https://mypy.readthedocs.io/en/stable/mypy_daemon.html)
- [github.com/facebook/pyre-check](https://github.com/facebook/pyre-check) ·
  [pyre-check on PyPI](https://pypi.org/project/pyre-check/)
- [github.com/google/pytype](https://github.com/google/pytype) ·
  [sunset issue #1925](https://github.com/google/pytype/issues/1925)
- [python/typing conformance suite](https://github.com/python/typing/blob/main/conformance/README.md) ·
  [PEP 729 (Typing Council)](https://peps.python.org/pep-0729/) ·
  [PEP 561](https://peps.python.org/pep-0561/)

**Vendor announcements & benchmarks:**
- [Astral: ty beta (Dec 2025)](https://astral.sh/blog/ty)
- [Meta: introducing Pyrefly (May 2025)](https://engineering.fb.com/2025/05/15/developer-tools/introducing-pyrefly-a-new-type-checker-and-ide-experience-for-python/)
- [Pyrefly: speed & memory comparison](https://pyrefly.org/blog/speed-and-memory-comparison/) ·
  [typing conformance comparison](https://pyrefly.org/blog/typing-conformance-comparison/) ·
  [lessons from Pyre](https://pyrefly.org/blog/lessons-from-pyre)

**Surveys & independent analysis:**
- [Typed Python 2024 survey (Meta)](https://engineering.fb.com/2024/12/09/developer-tools/typed-python-2024-survey-meta/)
- [Python Typing Survey 2025 (Meta)](https://engineering.fb.com/2025/12/22/developer-tools/python-typing-survey-2025-code-quality-flexibility-typing-adoption/)
- [Rob's deep dive: future Python type checkers](https://sinon.github.io/future-python-type-checkers/)
- [Posit/Positron: comparing Python type checkers (Mar 2026)](https://opensource.posit.co/blog/2026-03-31_python-type-checkers/)
- [Edward Li: Pyrefly vs ty](https://blog.edward-li.com/tech/comparing-pyrefly-vs-ty/)
- [pydevtools: how do mypy, pyright & ty compare?](https://pydevtools.com/handbook/explanation/how-do-mypy-pyright-and-ty-compare/)
- [Simon Willison on ty](https://simonwillison.net/2025/Dec/16/ty/)

*Sourcing caveat: several primary pages (vendor blogs, htmlpreview of the
conformance results, survey landing pages) are bot-protected and returned HTTP
403 to automated fetching; figures from those were cross-checked against
directly-verifiable sources (GitHub release APIs, PyPI, raw conformance file)
where possible. Benchmark multipliers and conformance percentages are
version-dependent — treat them as "as of mid-2026."*
