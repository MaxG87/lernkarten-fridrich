# Lernkarten zur Lösung eines Zauberwürfels nach der Fridrich-Methode

Dieses Projekt ermöglicht die Erstellung Lernkarten zur Erlernung der für die
Lösung eines Zauberwürfels nach Fridrich-Methode nötigen Schrittfolgen. Hierbei
wurde darauf geachtet, dass alle Seiten exakt dem selben Format entsprechen.
Dadurch können die Lernkarten sehr bequem in großen Stapeln zurechtgeschnitten
werden.

## Generierung der Lernkarten

Das Projekt generiert automatisch Lernkarten für verschiedene Algorithmen-Sets 
(PLL, OLL, oder größere Würfel) inklusive einer LaTeX-Datei für den Druck.

### Voraussetzungen

- Python 3.13 oder höher
- `uv` Package Manager (empfohlen) oder `pip`

### Installation

```bash
# Mit uv (empfohlen)
uv sync

# Oder mit pip
pip install -e .
```

### Verwendung

Das Kommando `generate-card-sets` erstellt SVG-Icons, Anki-CSV und eine 
LaTeX-Datei für physische Lernkarten:

```bash
# Generiere PLL-Karten mit Pfeilen
uv run generate-card-sets pll-with-arrows/ --algorithm-set pll

# Generiere OLL-Karten
uv run generate-card-sets oll/ --algorithm-set oll

# Generiere alle Algorithmen
uv run generate-card-sets output/ --algorithm-set all
```

Die automatisch generierte `Lernkarten.tex` Datei ist für zweiseitigen Druck 
optimiert:
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
