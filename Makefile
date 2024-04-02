BILDER = $(wildcard icon-*.png)
ALGOS = $(wildcard algo-*.tex)

%.pdf: %.tex $(BILDER) $(ALGOS)
	latexmk -lualatex PLL-Lernkarten.tex
