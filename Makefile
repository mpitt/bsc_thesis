all: pdf

pdf: thesis.pdf

thesis.pdf: thesis.md
	pandoc -s -S -o thesis.pdf --latex-engine xelatex --toc -V documentclass=memoir -V classoption=article -V classoption=oneside --filter pandoc-citeproc thesis.md
