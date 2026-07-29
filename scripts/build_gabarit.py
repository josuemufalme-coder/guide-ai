# -*- coding: utf-8 -*-
"""Construit le gabarit + les fragments a partir du document officiel d'origine."""
import os, re, shutil, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _scan as scan

SRC = sys.argv[1]
OUT = sys.argv[2]           # dossier modeles/
os.makedirs(os.path.join(OUT, 'fragments'), exist_ok=True)

zin = zipfile.ZipFile(SRC)
xml = zin.read('word/document.xml').decode('utf8')
P = scan.top_paragraphs(xml)

def frag(i):
    a, b = P[i]
    return xml[a:b]

def rpr_of(run):
    m = re.search(r'<w:rPr>.*?</w:rPr>', run, re.S)
    return m.group(0) if m else ''

def make_run(rpr, text):
    return '<w:r>' + rpr + '<w:t xml:space="preserve">' + text + '</w:t></w:r>'

def collapse(i, first, last, text, rpr_from=None):
    """Dans le paragraphe i, remplace les runs [first..last] par un seul run."""
    f = frag(i)
    runs = scan.top_runs(f)
    src = runs[rpr_from if rpr_from is not None else first]
    rpr = rpr_of(f[src[0]:src[1]])
    return f[:runs[first][0]] + make_run(rpr, text) + f[runs[last][1]:]

def pPr_of(f):
    m = re.search(r'<w:pPr>.*?</w:pPr>', f, re.S)
    return m.group(0) if m else ''

def p_open_of(f):
    return re.match(r'<w:p\b[^>]*>', f).group(0)

def skeleton(i, run_index):
    """Squelette de paragraphe : balise <w:p ...>, son pPr, un run vide {{RUNS}}."""
    f = frag(i)
    return p_open_of(f) + pPr_of(f) + '{{RUNS}}</w:p>', rpr_of(f[slice(*scan.top_runs(f)[run_index])])

# ---- fragments reutilisables (octet pour octet depuis l'original) -------------
def write(name, data):
    with open(os.path.join(OUT, 'fragments', name), 'w', encoding='utf8') as fh:
        fh.write(data)

sk_ouv, rpr_ouv = skeleton(12, 1)   # formule d'ouverture (ind droite 322, line 240)
sk_par, rpr_par = skeleton(16, 0)   # paragraphe de corps (after 160, line 259)
write('ouverture.xml', sk_ouv)
write('ouverture.rpr.xml', rpr_ouv)
write('paragraphe.xml', sk_par)
write('paragraphe.rpr.xml', rpr_par)
write('espace.xml', frag(15))            # separateur standard (line 259)
write('espace_ouverture.xml', frag(13))  # separateur apres la formule d'ouverture (line 240)

# ---- gabarit : insertion des jetons ------------------------------------------
new = xml
edits = []   # (span, remplacement) appliques de la fin vers le debut

# date
edits.append((P[0], frag(0).replace(
    '<w:t xml:space="preserve">, le </w:t>',
    '<w:t xml:space="preserve">, le {{DATE}}</w:t>')))
# numero d'enregistrement
edits.append((P[2], collapse(2, 7, 18,
    'N˚ {{NUMERO}}/MDNAC/RAD/Coord Nat/DAL/Div Num/{{ANNEE}}')))
# destinataire
edits.append((P[7], collapse(7, 0, 8, '           {{DESTINATAIRE}}', rpr_from=8)))
# objet
edits.append((P[10], collapse(10, 3, 5, '{{OBJET}}', rpr_from=3)))
# corps : tout le bloc p12..p22 devient un seul paragraphe porteur du jeton
edits.append(((P[12][0], P[22][1]), sk_par.replace('{{RUNS}}', make_run(rpr_par, '{{CORPS}}'))))
# signataire
edits.append((P[25], collapse(25, 2, 2, '{{SIGNATAIRE}}')))
# fonction
edits.append((P[26], collapse(26, 0, 3, '                   {{FONCTION}}')))

for (a, b), rep in sorted(edits, key=lambda e: -e[0][0]):
    new = new[:a] + rep + new[b:]

# ---- ecriture du .docx gabarit ----------------------------------------------
dst = os.path.join(OUT, 'lettre_officielle_RAD.gabarit.docx')
if os.path.exists(dst):
    os.remove(dst)
zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename == 'word/document.xml':
        data = new.encode('utf8')
    zout.writestr(item, data)
zout.close()
zin.close()

# ---- controle ---------------------------------------------------------------
txt = scan.text_of(new)
for tok in ['{{DATE}}', '{{NUMERO}}', '{{ANNEE}}', '{{DESTINATAIRE}}', '{{OBJET}}',
            '{{CORPS}}', '{{SIGNATAIRE}}', '{{FONCTION}}']:
    assert txt.count(tok) == 1, (tok, txt.count(tok))
print('gabarit ecrit :', dst)
print('texte du gabarit :')
print(re.sub(r'[ \t]+', ' ', txt))
