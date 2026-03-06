---
name: using-terminal-charts
description: This skill should be used when the user asks to "visualize data", "render a chart", "plot numbers", "show a graph in terminal", "create a bar chart", "make a sparkline", "draw a heatmap", or needs to display numeric data as terminal charts using chartli. Also triggers on "chartli", "terminal chart", "ASCII chart", "braille chart".
---

# Terminal Charts with chartli

Render numeric data as terminal charts using `chartli` — supports ASCII line, sparklines, horizontal bars, columns, heatmap, unicode bars, braille, and SVG output.

## Quick Reference

```sh
npx chartli <file> -t <type> [-w <width>] [-h <height>] [-m <mode>]
```

| Type | Best For | Key Options |
|------|----------|-------------|
| `ascii` | Line charts with axes | `-w` width, `-h` height |
| `spark` | Compact inline trends | (none) |
| `bars` | Horizontal bar comparison | `-w` width |
| `columns` | Vertical bar comparison | `-h` height |
| `heatmap` | Multi-series density view | (none) |
| `unicode` | Detailed vertical bars | (none) |
| `braille` | High-density scatter/line | `-w` width, `-h` height |
| `svg` | File export, embedding | `-m circles\|lines`, `-w`, `-h` |

## Input Data Format

Whitespace-separated numeric rows. Optional header row (non-numeric first row is treated as labels).

### Single Series

```text
day value
1 10
2 20
3 15
4 30
5 25
```

### Multi Series

```text
day sales costs profit
1 10 8 2
2 14 9 5
3 12 11 3
4 18 10 8
```

Multi-series data renders separate series for `spark`, `bars`, `heatmap`, and `unicode` types. Single-series types (`ascii`, `braille`) use the first numeric column.

## Usage Patterns

### From File

```sh
npx chartli data.txt -t ascii -w 40 -h 10
npx chartli data.txt -t spark
npx chartli data.txt -t bars -w 28
```

### From Stdin (pipe)

```sh
printf 'x y\n1 10\n2 20\n3 15\n4 30\n' | npx chartli -t ascii -w 24 -h 8
```

### From Command Output

Generate a temp data file from any command output, then chart it:

```sh
# Line counts per file
wc -l src/*.ts | grep -v total | awk '{print NR, $1}' > /tmp/chart-data.txt
npx chartli /tmp/chart-data.txt -t bars -w 30

# Git commits per day (last 30 days)
git log --since="30 days ago" --format='%ad' --date=short | sort | uniq -c | awk '{print NR, $1}' > /tmp/chart-data.txt
npx chartli /tmp/chart-data.txt -t ascii -w 40 -h 10

# Process memory usage over time
ps aux | sort -k4 -rn | head -10 | awk '{print NR, $4}' > /tmp/chart-data.txt
npx chartli /tmp/chart-data.txt -t bars -w 30
```

### SVG Export

```sh
npx chartli data.txt -t svg -m lines -w 320 -h 120 | sed -n '/^<?xml/,$p' > chart.svg
```

The `sed` filter strips the chartli banner. Use `-m circles` (default) or `-m lines` for SVG style.

## Type Selection Guide

- **Quick trend overview** → `spark` (most compact, one line per series)
- **Values with axes** → `ascii` (classic line chart with scale)
- **Compare magnitudes** → `bars` (horizontal) or `columns` (vertical)
- **Dense multi-series** → `heatmap` (grid with shading) or `unicode` (grouped vertical bars)
- **High resolution** → `braille` (2x4 dot matrix per character cell)
- **Export/embed** → `svg` (vector output for docs/web)

## Common Dimensions

| Context | Suggested |
|---------|-----------|
| Inline / compact | `-w 24 -h 6` |
| Standard terminal | `-w 40 -h 10` |
| Wide terminal | `-w 60 -h 15` |
| SVG export | `-w 320 -h 120` |

## Notes

- `npx chartli` auto-installs on first run (no global install needed)
- Banner header prints to stdout — use `2>/dev/null` to suppress stderr, or `sed -n '/^<?xml/,$p'` for SVG
- All numeric values are normalized to 0–1 range internally
- Empty or non-numeric rows are skipped
