BILDER = $(wildcard icon-*.png)
ALGOS = $(wildcard algo-*.tex)

.PHONY: all
all: PLL-Lernkarten.pdf

%.pdf: %.tex $(BILDER) $(ALGOS)
	latexmk -lualatex PLL-Lernkarten.tex
