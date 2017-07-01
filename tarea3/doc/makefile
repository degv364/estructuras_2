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
	rm -r reporte.pdf

clean_all:
	rm -r *.aux *.log *.bbl *.blg reporte.pdf
