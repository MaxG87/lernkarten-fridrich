ALGOS = $(wildcard algo-*.tex)
BILDER = $(subst algo,icon,$(patsubst %.tex,%.pdf,$(ALGOS)))

OLL_ALGOS = $(wildcard oll-*.tex,$(ALGOS))
OLL_BILDER = $(OLL_ALGOS:.tex=.pdf)
PLL_ALGOS = $(wildcard pll-*.tex,$(ALGOS))
PLL_BILDER = $(PLL_ALGOS:.tex=.pdf)

Lernkarten.pdf: Lernkarten.tex $(BILDER) $(ALGOS)
	latexmk -lualatex Lernkarten.tex

%.pdf: %.svg
	inkscape --export-filename $@ $<

%.svg: %.tex
	fname='$<'; \
	      stage=$${fname%-*}; \
	      echo $$stage; \
	      tr -Cd "RLUDFB'2" < $< |\
		sed "s!^!http://cube.rider.biz/visualcube.php?size=300\&fmt=svg\&pzl=3\&stage=$${stage}\&view=plan\&alg=!" |\
		xargs wget -O $@
