REPRODUCE = python scripts/reproduce_all.py
TEX = paper/Not All Attention Is Equal.tex

.PHONY: reproduce paper check clean

## reproduce: run the full EEI analysis pipeline (env check + Table 6 + composites + null model)
reproduce:
	$(REPRODUCE)

## paper: compile the manuscript PDF (pdflatex, 2 passes)
paper:
	cd paper && pdflatex -interaction=nonstopmode -halt-on-error "Not All Attention Is Equal.tex" && pdflatex -interaction=nonstopmode -halt-on-error "Not All Attention Is Equal.tex"

## check: verify manuscript integrity, committed-table fidelity, and the environment
check:
	python scripts/check_manuscript_sync.py
	python scripts/eei_sensitivity.py --scores data/eei_scores.csv --inclusion-ledger data/method_metadata.csv --check-latex results/tables/tab_eei_sensitivity.tex

## clean: remove LaTeX build artifacts
clean:
	rm -f paper/*.aux paper/*.log paper/*.out paper/*.toc paper/*.lof paper/*.lot paper/*.fls paper/*.fdb_latexmk paper/*.synctex.gz