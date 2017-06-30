all: reporte.pdf

first: reporte.tex bibliografia.bib
	pdflatex reporte.tex
	pdflatex reporte.tex
	pdflatex reporte.tex
	bibtex reporte
	pdflatex reporte.tex
	pdflatex reporte.tex
	pdflatex reporte.tex

reporte.pdf: reporte.tex bibliografia.bib
	pdflatex reporte.tex
	bibtex reporte
	pdflatex reporte.tex

clean:
	rm reporte.pdf

clean_all:
	rm *.aux *.log *.bbl *.blg reporte.pdf
