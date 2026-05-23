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

## Installation

1. Copy folder inside your Anki addons directory:
   - Windows: `%APPDATA%\Anki2\addons21\`
2. Restart Anki

## Compatibility

Anki 23.x / 24.x / 25.x
