ALGOS = $(wildcard algo-*.tex)
BILDER = $(subst algo,icon,$(patsubst %.tex,%.pdf,$(ALGOS)))

OLL_ALGOS = $(wildcard oll-*.tex,$(ALGOS))
OLL_BILDER = $(patsubst %.tex,%.pdf,$(OLL_ALGOS))

Lernkarten.pdf: Lernkarten.tex $(BILDER) $(ALGOS)
	latexmk -lualatex Lernkarten.tex

oll-%.pdf: oll-%.svg
	inkscape --export-filename $@ $<

oll-%.svg: oll-%.tex
	cat $< |\
		tr -Cd "RLUDFB'2" |\
		sed 's!^!http://cube.rider.biz/visualcube.php?size=300\&fmt=svg\&pzl=3\&stage=oll\&view=plan\&alg=!' |\
		xargs wget -O $@
