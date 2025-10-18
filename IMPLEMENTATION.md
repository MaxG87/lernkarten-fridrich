# LaTeX Generation for Physical Learning Cards

## Overview

This implementation adds a new feature to the `generate-algorithm-cards.py` script that generates a LaTeX document for printing physical learning cards.

## Key Features

### 1. Two-Sided Card Layout
- **Odd pages**: Display cube state icons (front of cards)
- **Even pages**: Display algorithms (back of cards)
- **Alignment**: Algorithms are horizontally reversed to align correctly when printed back-to-back

### 2. Flexible Grid Layout
- Configurable cards per row and column (default: 3x3 grid = 9 cards per page)
- Automatically handles partial pages (when total cards don't fill the grid)
- Each card has equal dimensions for easy batch cutting

### 3. Algorithm Formatting
- Converts cube notation to proper LaTeX format
- Handles primes (R' becomes R')
- Handles number suffixes (R2 becomes R²)
- Handles wide moves (Rw, Uw, etc.)
- Handles prefix numbers (2R, 3L, etc.)

### 4. Integration
- Adds `--generate-latex` flag to the main script
- Works with all algorithm sets (PLL, OLL, big-cube, all)
- Generates `Lernkarten.tex` in the output directory

## Technical Details

### Functions Added

1. **`escape_latex(text: str) -> str`**
   - Escapes special LaTeX characters in text
   - Used for algorithm names and text content

2. **`algorithm_to_latex(alg: Algorithm) -> str`**
   - Converts cube notation to LaTeX math mode
   - Handles complex move patterns using regex
   - Example: `R U R' U'` → `R U $\text{R}'$ $\text{U}'$`

3. **`create_latex_document(...)`**
   - Main function that generates the complete LaTeX document
   - Parameters:
     - `algorithms`: List of algorithm configurations
     - `case_fnames`: Dictionary mapping algorithms to icon paths
     - `latex_fname`: Output file path
     - `cards_per_row`: Horizontal card count (default: 3)
     - `cards_per_col`: Vertical card count (default: 3)

### LaTeX Document Structure

```latex
\documentclass[12pt,a4paper,landscape]{scrartcl}
% Preamble with packages and custom commands
\begin{document}
  % Page 1: Icons (3x3 grid)
  % Page 2: Algorithms (3x3 grid, reversed)
  % Page 3: Icons (next batch)
  % Page 4: Algorithms (next batch, reversed)
  % ...
\end{document}
```

### Reversal Logic

For a row with cards A, B, C:
- Front page (icons): A | B | C
- Back page (algorithms): C | B | A

This ensures that when printed double-sided and cut, each algorithm appears on the back of its corresponding icon.

## Usage

### Command Line

```bash
# Generate PLL cards with LaTeX
python scripts/generate-algorithm-cards.py pll-with-arrows/ \
  --algorithm-set pll \
  --generate-latex

# Generate OLL cards with LaTeX
python scripts/generate-algorithm-cards.py oll/ \
  --algorithm-set oll \
  --generate-latex

# Generate all algorithms with LaTeX
python scripts/generate-algorithm-cards.py output/ \
  --algorithm-set all \
  --generate-latex
```

### Compiling the LaTeX

```bash
cd pll-with-arrows/  # or your output directory
lualatex Lernkarten.tex
```

The generated PDF can then be printed double-sided and cut into individual cards.

## Testing

Three test files validate the implementation:

1. **`test_latex_functionality.py`**
   - Tests algorithm parsing
   - Tests LaTeX structure
   - Tests reversal logic

2. **`test_integration.py`**
   - Full integration test
   - Creates test data and verifies complete workflow
   - Validates generated LaTeX content

3. **`example_latex_generation.py`**
   - Shows usage examples
   - Documents the API

All tests pass without requiring external dependencies (except Python stdlib).

## Comparison with Original `lernkarten-pdf/Lernkarten.tex`

### Original Approach
- Hardcoded for exactly 89 algorithms
- Uses numbered icon and algorithm files (icon-01.png, algo-01.tex)
- Manual page layout with specific counter manipulation
- Not flexible for different sets of algorithms

### New Approach
- Works with any number of algorithms
- Uses SVG icons generated dynamically
- Automatic page layout based on algorithm count
- Works with any algorithm set (PLL, OLL, big-cube)
- Algorithms formatted directly in the LaTeX file (no separate .tex files needed)
- Configurable grid size

## Benefits

1. **Flexibility**: Generate cards for any algorithm set
2. **Maintainability**: One source of truth for algorithms
3. **Consistency**: Same icons used for Anki and physical cards
4. **Automation**: No manual LaTeX editing needed
5. **Scalability**: Easy to add new algorithms
