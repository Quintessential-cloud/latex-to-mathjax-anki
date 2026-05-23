# LaTeX to MathJax for Anki

An Anki addon that automatically converts LaTeX dollar-sign notation to MathJax delimiters while you type or paste.

## What it does

| Input | Output |
|-------|--------|
| `$x^2$` | `\(x^2\)` |
| `$$x^2$$` | `\[x^2\]` |
| `\begin{equation}...\end{equation}` | `\[...\]` |
| `\begin{align}...\end{align}` | `\[\begin{aligned}...\end{aligned}\]` |

Already-converted expressions (`\(...\)`, `\[...\]`) are left untouched.

## Features

- **Toggle button** — `MJ ○ / MJ ●` in the editor toolbar to enable or disable conversion
- **Paste** — converts on paste via JavaScript
- **Typing** — converts ~1 second after you stop typing via Anki's typing timer hook

## Installation

1. Copy `__init__.py` and `manifest.json` into a new folder inside your Anki addons directory:
   - Windows: `%APPDATA%\Anki2\addons21\latex_mathjax\`
2. Restart Anki

## Compatibility

Anki 23.x / 24.x / 25.x
