all: pdf

pdf: thesis.pdf

thesis.pdf: thesis.aux thesis.toc frontespizio.tex
	xelatex thesis.tex

thesis.aux thesis.toc: thesis.tex
	xelatex thesis.tex
