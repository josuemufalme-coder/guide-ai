#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exporte le .docx en PDF en forcant d'abord le calcul de la table des matieres.

LibreOffice en mode sans interface n'execute pas la mise a jour des champs,
meme lorsque le document la demande. On passe donc par une macro Basic qui
charge le document, met a jour les index et les champs, puis exporte.

Usage : python3 outils/exporter_pdf.py fichier.docx
"""
import shutil
import subprocess
import sys
from pathlib import Path

MACRO = '''
Sub ExporterAvecTdm(cheminEntree As String, cheminSortie As String)
    Dim props(0) As New com.sun.star.beans.PropertyValue
    props(0).Name = "Hidden" : props(0).Value = True
    doc = StarDesktop.loadComponentFromURL(cheminEntree, "_blank", 0, props())

    ' Mise a jour des index (table des matieres) puis de tous les champs.
    If Not IsNull(doc.getDocumentIndexes()) Then
        For i = 0 To doc.getDocumentIndexes().getCount() - 1
            doc.getDocumentIndexes().getByIndex(i).update()
        Next i
    End If
    If Not IsNull(doc.getTextFields()) Then
        doc.getTextFields().refresh()
    End If
    doc.reformat()

    Dim expo(0) As New com.sun.star.beans.PropertyValue
    expo(0).Name = "FilterName" : expo(0).Value = "writer_pdf_Export"
    doc.storeToURL(cheminSortie, expo())
    doc.close(False)
End Sub
'''


def exporter(docx):
    docx = Path(docx).resolve()
    pdf = docx.with_suffix(".pdf")

    base = Path.home() / ".config/libreoffice/4/user/basic/Standard"
    base.mkdir(parents=True, exist_ok=True)
    (base / "Module1.xba").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" '
        '"module.dtd">\n'
        '<script:module xmlns:script="http://openoffice.org/2000/script" '
        'script:name="Module1" script:language="StarBasic">'
        + MACRO.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") +
        "</script:module>", encoding="utf-8")
    (base / "script.xlb").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE library:library PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" '
        '"library.dtd">\n'
        '<library:library xmlns:library="http://openoffice.org/2000/library" '
        'library:name="Standard" library:readonly="false" library:passwordprotected="false">'
        '<library:element library:name="Module1"/></library:library>', encoding="utf-8")

    url_in = docx.as_uri()
    url_out = pdf.as_uri()
    cmd = ["soffice", "--headless", "--norestore", "--invisible",
           f'macro:///Standard.Module1.ExporterAvecTdm("{url_in}","{url_out}")']
    if pdf.exists():
        pdf.unlink()
    subprocess.run(cmd, capture_output=True, timeout=900)
    if pdf.exists():
        print(f"  {pdf.name} ({pdf.stat().st_size // 1024} Ko) --- table des matieres calculee")
        return pdf
    # Repli : export simple, sans table des matieres remplie.
    print("  [!] Macro sans effet, repli sur l'export simple (table non remplie).")
    subprocess.run(["soffice", "-env:UserInstallation=file:///tmp/lo_manuel",
                    "--headless", "--norestore", "--convert-to", "pdf",
                    "--outdir", str(docx.parent), str(docx)],
                   capture_output=True, timeout=900)
    return pdf if pdf.exists() else None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(0 if exporter(sys.argv[1]) else 1)
