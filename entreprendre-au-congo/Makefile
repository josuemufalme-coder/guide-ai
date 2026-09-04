# « Entreprendre au Congo » — chaîne de fabrication.
#
# Le cahier des charges exige qu'une seule commande régénère les cinq livrables
# sur une machine vierge : `make tout`. Chaque cible reste indépendante pour
# permettre de rejouer une phase sans tout recompiler.
#
# État : phase 0. Le manuscrit est reconstitué et contrôlé ; le gabarit
# typographique de la phase 1 n'est pas encore posé, et les cibles qui en
# dépendent le disent plutôt que de produire un fichier trompeur.

SHELL     := /bin/bash
SOURCE    := source
SRC       := src
QA        := qa
BUILD     := build
PDFS      := $(SOURCE)/ENTREPRENDRE-AU-CONGO-p001-072.pdf \
             $(SOURCE)/ENTREPRENDRE-AU-CONGO-p073-144.pdf
EXTRACTION := $(SOURCE)/ENTREPRENDRE-AU-CONGO-extraction.txt
CHAPITRES := $(wildcard $(SRC)/*.md)

APT := texlive-luatex texlive-lang-french texlive-latex-extra texlive-fonts-extra \
       texlive-pictures texlive-plain-generic latexmk fonts-ebgaramond \
       poppler-utils python3-pip

.PHONY: aide setup reconstituer integrite structure mesures qa livre epub relecture tout propre

aide:
	@echo "cibles :"
	@echo "  setup         installe la chaîne (LuaLaTeX, poppler, polices)"
	@echo "  reconstituer  régénère src/*.md depuis le PDF de contrôle"
	@echo "  integrite     vérifie que la reconstitution ne perd aucun signe"
	@echo "  structure     vérifie l'agencement : titres, encadrés, tableaux"
	@echo "  mesures       relève césure, ponctuation haute, gabarit"
	@echo "  qa            integrite + mesures, rapports archivés dans qa/"
	@echo "  livre         interieur.pdf            (phase 1)"
	@echo "  epub          livre.epub               (phase 9)"
	@echo "  relecture     relecture.pdf            (phase 9)"
	@echo "  tout          l'ensemble des livrables (phase 9)"

setup:
	apt-get update -qq
	apt-get install -y -qq $(APT)
	python3 -m pip install --quiet --break-system-packages pypdf

# --- Phase 0 : reconstitution et contrôle ---------------------------------

reconstituer:
	python3 $(QA)/reconstituer.py $(PDFS) --sortie $(SRC)

integrite: | $(BUILD)
	python3 $(QA)/verifier-integrite.py --reference $(EXTRACTION) --source $(SRC) \
	  | tee $(QA)/rapport-integrite.txt

mesures: | $(BUILD)
	python3 $(QA)/mesure-typo.py $(PDFS) | tee $(QA)/mesures-pdf-existant.txt

structure: | $(BUILD)
	python3 $(QA)/verifier-structure.py $(PDFS) --source $(SRC) \
	  | tee $(QA)/rapport-structure.txt

qa: integrite structure mesures

$(BUILD):
	@mkdir -p $(BUILD)

# --- Phases suivantes ------------------------------------------------------

livre epub relecture tout:
	@echo "Cible « $@ » : le gabarit typographique de la phase 1 n'est pas encore"
	@echo "posé. Rien n'est produit plutôt qu'un fichier qui ne vaudrait rien."
	@exit 1

propre:
	rm -rf $(BUILD)
