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

## Mögliche Verbesserungen

* Die Bilder sind teils etwas unscharf. Diese könnten mittels TikZ als
  Vektorgrafik generiert werden.
* Es ist momentan nur großer Sorgfalt zu verdanken, dass die Algorithmen zu den
  Bildern passen. Es könnte überlegt werden, dies irgendwie programmatisch
  sicherzustellen.

## Lizenz

Sowohl die Schrittfolgen als auch die Bilder sind Anleitungen von
https://www.kungfoomanchu.com/ entnommen. Sie wurden hier nur neu
zusammengesetzt.
