ICON_FTYPE := eps

OLL_ALGOS = $(wildcard oll-*.tex)
OLL_BILDER = $(OLL_ALGOS:.tex=.$(ICON_FTYPE))
PLL_ALGOS = $(wildcard pll-*.tex)
PLL_BILDER = $(PLL_ALGOS:.tex=.$(ICON_FTYPE))

ALGOS = $(OLL_ALGOS) $(PLL_ALGOS)
BILDER = $(OLL_BILDER) $(PLL_BILDER)


Lernkarten.pdf: Lernkarten.tex $(BILDER) $(ALGOS)
	latexmk -lualatex Lernkarten.tex

%.$(ICON_FTYPE): %.svg
	inkscape --export-filename $@ $<

%.svg: %.tex
	fname='$<'; \
	      stage=$${fname%-*}; \
	      echo $$stage; \
	      tr -Cd "RLUDFB'2" < $< |\
		sed "s!^!http://cube.rider.biz/visualcube.php?size=300\&fmt=svg\&pzl=3\&stage=$${stage}\&view=plan\&alg=!" |\
		xargs wget -O $@

icon-%.$(ICON_FTYPE): oll-%.$(ICON_FTYPE)
	cp $< $@

icon-%.$(ICON_FTYPE): pll-%.$(ICON_FTYPE)
	cp $< $@
