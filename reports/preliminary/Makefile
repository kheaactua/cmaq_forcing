# Generic make file for LaTeX: requires GNU make
#
# Downloaded at:
# http://www.math.umbc.edu/~rouben/prosper/makefile.html

TEXFILE	:= prototype.tex
PDFFILE := ${TEXFILE:.tex=.pdf}
RTFFILE  := ${TEXFILE:.tex=.rtf}

hostname=$(shell hostname)
ifeq ($(hostname),pontus.cee.carleton.ca)
#PDF_CMD := /opt/local/libexec/texlive/texbin/pdflatex
PDF_CMD := /usr/local/texlive/2010/bin/x86_64-darwin/pdflatex --shell-escape
else
PDF_CMD := pdflatex --shell-escape
endif

.PHONY: clean lclean
.SUFFIXES: .tex .pdf

all: build view
build: $(PDFFILE)

view:
ifeq ($(hostname),pontus.cee.carleton.ca)
	open $(PDFFILE);
else
	evince $(PDFFILE);
endif


${PDFFILE}:	${TEXFILE}

%.pdf: %.tex
	$(PDF_CMD) $<;
	$(PDF_CMD) $<;
	while grep -q "Rerun to get cross-references right." $(<:.tex=.log); \
	do \
		$(PDF_CMD) $<; \
	done
	$(PDF_CMD) $<;

${RTFFILE}: ${PDFFILE}
	latex2rtf ${TEXFILE};
	cp ${TEXFILE:.tex=.rtf} ${RTFFILE}

lclean:
	rm $(TEXFILE:.tex=.pdf)

clean:
	@rm -f \
	*.aux \
	$(TEXFILE:.tex=.log) \
	$(TEXFILE:.tex=.out) \
	$(TEXFILE:.tex=.dvi) \
	$(PDFFILE) \
	${RTFFILE} \
	$(TEXFILE:.tex=.bib) \
	$(TEXFILE:.tex=.bbl) \
	$(TEXFILE:.tex=.blg) \
	$(TEXFILE:.tex=.toc) \
	$(TEXFILE:.tex=.ilg) \
	$(TEXFILE:.tex=.idx) \
	$(TEXFILE:.tex=.ind) \
	$(TEXFILE:.tex=.lof) \
	$(TEXFILE:.tex=.lot) \
	$(TEXFILE:.tex=.ps)
