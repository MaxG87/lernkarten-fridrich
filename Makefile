ICON_FTYPE := pdf

OLL_ALGOS = $(wildcard oll-*.tex)
OLL_BILDER = $(OLL_ALGOS:.tex=.$(ICON_FTYPE))
PLL_ALGOS = $(wildcard pll-*.tex)
PLL_BILDER = $(PLL_ALGOS:.tex=.$(ICON_FTYPE))

ALGOS = $(subst oll,algo,$(OLL_ALGOS)) $(subst pll,algo,$(PLL_ALGOS))
BILDER = $(subst oll,icon,$(OLL_BILDER)) $(subst pll,icon,$(PLL_BILDER))


Lernkarten.pdf: Lernkarten.tex $(BILDER) $(ALGOS)
	latexmk -lualatex Lernkarten.tex

%.$(ICON_FTYPE): %.svg
	inkscape --export-filename $@ $<

%.svg: %.url
	wget -O $@ "$$(cat $<)"

%.url: %.tex
	fname='$<'; \
	      stage=$${fname%-*}; \
	      head -n 1 $< | \
	      sed 's/\\text//g' |\
	      tr -d '^(){}$$ \\' |\
	      sed "s!^!http://cube.rider.biz/visualcube.php?size=300\&fmt=svg\&pzl=3\&stage=$${stage}\&view=plan\&case=!" > $@

icon-%: oll-%
	cp $< $@

icon-%: pll-%
	cp $< $@

algo-%.tex: oll-%.tex
	cp $< $@

algo-%.tex: pll-%.tex
	cp $< $@
