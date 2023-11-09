BILDER = $(wildcard icon-*.png)
ALGOS = $(wildcard algo-*.tex)

.PHONY: all
all: Lernkarten.pdf

%.pdf: %.tex $(BILDER) $(ALGOS)
	latexmk -lualatex Lernkarten.tex
