# COM726 dissertation build
LATEXMK = latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build

.PHONY: all clean wc check

all:
	$(LATEXMK) main.tex
	@cp build/main.pdf ./Dissertation_COM726_Shubham.pdf 2>/dev/null || true
	@echo "--> Dissertation_COM726_Shubham.pdf"

clean:
	latexmk -C -outdir=build
	rm -f Dissertation_COM726_Shubham.pdf

# Body word count excluding figures/references, per the assessment brief
wc:
	@which texcount >/dev/null 2>&1 && texcount -inc -sum -q main.tex || \
		echo "texcount not installed; run: tlmgr install texcount"

# Pre-submission checks
check:
	@echo "== undefined references / citations =="
	@grep -iE "undefined (reference|citation)" build/main.log || echo "  none"
	@echo "== overfull boxes =="
	@grep -c "Overfull" build/main.log || echo "  0"
	@echo "== residual [source:] tags in .tex =="
	@grep -rn "\[source:" chapters/ appendices/ || echo "  none"
	@echo "== UNFILLED PLACEHOLDERS (must be zero before submission) =="
	@grep -rn "\[INSERT\|\[CITE KEY\]\|\[VERIFY LICENCE\]\|\[TODO" \
		chapters/ appendices/ frontmatter/ || echo "  none"
