all: reporte.pdf

reporte.pdf: reporte.tex bibliografia.bib
	pdflatex reporte.tex
	pdflatex reporte.tex
	pdflatex reporte.tex
	bibtex reporte
	pdflatex reporte.tex
	pdflatex reporte.tex
	pdflatex reporte.tex

clean:
	rm *.aux *.log reporte.pdf
