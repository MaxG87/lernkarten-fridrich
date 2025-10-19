# Lernkarten zur Lösung eines Zauberwürfels nach der Fridrich-Methode

Dieses Projekt ermöglicht die Erstellung Lernkarten zur Erlernung der für die
Lösung eines Zauberwürfels nach Fridrich-Methode nötigen Schrittfolgen. Hierbei
wurde darauf geachtet, dass alle Seiten exakt dem selben Format entsprechen.
Dadurch können die Lernkarten sehr bequem in großen Stapeln zurechtgeschnitten
werden.

## Erstellung der PDF

Um eine PDF zu erstellen, wird ein funktionierendes LaTeX-Setup mit `lualatex`
vorausgesetzt. Ist dies gegeben, reicht zur Erstellung der PDF ein einfaches
`make`.

Sollte `make` nicht zur Verfügung stehen, kann auch manuell mehrfach `lualatex
Lernkarten.tex` ausgeführt werden.

## Generierung von physischen Lernkarten

Das Projekt enthält ein Skript zum Erstellen von Ordnern für physische Lernkarten.
Das Skript erstellt eine LaTeX-Datei und ein Makefile, die SVG-Dateien in PDF
konvertieren und die Lernkarten für den doppelseitigen Druck vorbereiten.

### Verwendung

```bash
python3 -m lernkarten_scripts.generate_physical_cards <zielordner>
```

Das Skript:
1. Erstellt die Dateien `Lernkarten.tex` und `Makefile` im Zielordner
2. Scannt nach vorhandenen Icon-Dateien (`icon-01.svg`, `icon-02.svg`, ...) und Algorithmus-Dateien (`algo-01.tex`, `algo-02.tex`, ...)
3. Generiert die LaTeX-Datei basierend auf der Anzahl der gefundenen Dateien

### Dateistruktur

Der Zielordner sollte folgende Dateien enthalten:
- `icon-01.svg`, `icon-02.svg`, ... (SVG-Dateien der Würfel-Icons)
- `algo-01.tex`, `algo-02.tex`, ... (LaTeX-Dateien mit den Algorithmen)

Nach dem Ausführen von `make` im Zielordner werden die SVG-Dateien in PDF konvertiert
und eine `Lernkarten.pdf` erstellt, die für den doppelseitigen Druck optimiert ist.

**Wichtig:** Die Algorithmen auf der Rückseite werden automatisch in umgekehrter
Reihenfolge angeordnet (z.B. für Icons A, B, C werden die Algorithmen C, B, A
gedruckt), um nach dem doppelseitigen Druck und Zuschneiden eine korrekte
Zuordnung zu gewährleisten.

## Lizenz

Sowohl die Schrittfolgen als auch die Bilder sind Anleitungen von
https://www.kungfoomanchu.com/ entnommen. Sie wurden hier nur neu
zusammengesetzt.
