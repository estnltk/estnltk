# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = _build

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .


.PHONY: clean
clean:
	rm -rf $(BUILDDIR)/*
	rm tutorials/*rst

.PHONY: html
html:
	#using jupyter to convert tutorial notebooks
	jupyter nbconvert --to rst tutorials/*ipynb  --output-dir tutorials

	python make_toc.py tutorials/index.rst "Estnltk tutorials">> temp #don't know why I can't overwrite it directly
	mv temp tutorials/index.rst

	#make a frontpage from index.rst
	pandoc ../README.md -o ./index.rst
	cat toc.rst >> index.rst

	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html 2> error.log
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

