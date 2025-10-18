# Lernkarten zur Lösung eines Zauberwürfels nach der Fridrich-Methode

Dieses Projekt ermöglicht die Erstellung Lernkarten zur Erlernung der für die
Lösung eines Zauberwürfels nach Fridrich-Methode nötigen Schrittfolgen. Hierbei
wurde darauf geachtet, dass alle Seiten exakt dem selben Format entsprechen.
Dadurch können die Lernkarten sehr bequem in großen Stapeln zurechtgeschnitten
werden.

## Generierung der Lernkarten

Das Python-Skript `scripts/generate-algorithm-cards.py` generiert automatisch
Lernkarten für verschiedene Algorithmen-Sets (PLL, OLL, oder größere Würfel).

### Voraussetzungen

- Python 3.13 oder höher
- Die benötigten Python-Pakete (siehe `pyproject.toml`)

### Verwendung

```bash
# Generiere PLL-Karten mit Pfeilen und LaTeX-Datei
python scripts/generate-algorithm-cards.py pll-with-arrows/ --algorithm-set pll --generate-latex

# Generiere OLL-Karten
python scripts/generate-algorithm-cards.py oll/ --algorithm-set oll --generate-latex

# Generiere alle Algorithmen
python scripts/generate-algorithm-cards.py output/ --algorithm-set all --generate-latex
```

Die `--generate-latex` Option erzeugt eine `Lernkarten.tex` Datei, die für
zweiseitigen Druck optimiert ist:
- Ungerade Seiten zeigen die Würfel-Icons (Vorderseite der Karten)
- Gerade Seiten zeigen die Algorithmen (Rückseite der Karten)
- Die Algorithmen sind horizontal gespiegelt angeordnet, damit sie beim
  beidseitigen Druck und Schneiden exakt ausgerichtet sind

## Erstellung der PDF

Um eine PDF zu erstellen, wird ein funktionierendes LaTeX-Setup mit `lualatex`
vorausgesetzt. Ist dies gegeben, reicht zur Erstellung der PDF ein einfaches
`make`.

Sollte `make` nicht zur Verfügung stehen, kann auch manuell mehrfach `lualatex
Lernkarten.tex` ausgeführt werden.

### Aus generierter LaTeX-Datei

Nach dem Generieren der LaTeX-Datei:

```bash
cd pll-with-arrows/  # oder das entsprechende Ausgabeverzeichnis
lualatex Lernkarten.tex
```

## Lizenz

Sowohl die Schrittfolgen als auch die Bilder sind Anleitungen von
https://www.kungfoomanchu.com/ entnommen. Sie wurden hier nur neu
zusammengesetzt.
