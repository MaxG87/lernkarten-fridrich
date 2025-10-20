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

Das Projekt enthält Funktionalität zum Erstellen von physischen Lernkarten als Teil des
`generate-algorithm-cards` Skripts. Das Skript erstellt eine LaTeX-Datei und ein Makefile,
die SVG-Dateien in PDF konvertieren und die Lernkarten für den doppelseitigen Druck vorbereiten.

### Verwendung

```bash
generate-algorithm-cards <zielordner> --algorithm-set <set> --generate-learning-cards
```

Beispiel für PLL-Karten:
```bash
generate-algorithm-cards pll-cards --algorithm-set pll --generate-learning-cards
```

Das Skript:
1. Lädt die SVG-Ikonen für die Algorithmen herunter
2. Erstellt eine CSV-Datei für Anki
3. Erstellt die Algorithmus-Dateien (`algo-01.tex`, `algo-02.tex`, ...)
4. Generiert `Lernkarten.tex` basierend auf den Algorithmen
5. Erstellt ein `Makefile` zum Kompilieren

### Dateistruktur

Nach dem Ausführen enthält der Zielordner:
- `icon-01.svg`, `icon-02.svg`, ... (heruntergeladene SVG-Dateien der Würfel-Icons)
- `algo-01.tex`, `algo-02.tex`, ... (generierte LaTeX-Dateien mit den Algorithmen)
- `Lernkarten.tex` (generierte LaTeX-Datei mit der Kartenlayout)
- `Makefile` (zum Kompilieren des PDFs)
- `ankiCardSet.csv` (für Anki-Import)

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
