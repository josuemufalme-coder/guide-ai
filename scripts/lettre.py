# -*- coding: utf-8 -*-
"""
Genere une lettre officielle RAD a partir du gabarit, sans jamais toucher a la
mise en page : le .docx d'origine est recopie octet pour octet et seuls les
textes sont substitues dans word/document.xml.

Usage :
    python3 scripts/lettre.py lettres/ma_lettre.txt
    python3 scripts/lettre.py lettres/ma_lettre.txt -o lettres/sortie.docx
    python3 scripts/lettre.py lettres/ma_lettre.txt --texte   # controle : affiche le texte final

Format du fichier d'entree (.txt, UTF-8) :

    OBJET: demande d'acquisition de trois onduleurs
    DESTINATAIRE: Au Dir AdmLog
    DATE: 29 juillet 2026
    NUMERO: 042
    ---
    En effet, dans le cadre de ...

    Ce document, joint en annexe ...

Les champs sont optionnels sauf OBJET. Les paragraphes du corps sont separes par
une ligne vide. La formule d'ouverture et la formule de politesse sont ajoutees
automatiquement (voir DEFAUTS ci-dessous) ; on peut les remplacer avec les
champs OUVERTURE: et CLOTURE:, ou les supprimer avec la valeur "aucune".

Enrichissements dans le corps :
    **gras**        -> gras
    __souligne__    -> souligne
    - element       -> puce (numId 1, tiret), retrait subordonne
Les paragraphes ordinaires sont numerotes 1., 2., 3. automatiquement par Word,
exactement comme dans le modele d'origine.
"""
import argparse
import datetime
import os
import re
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _scan as scan

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GABARIT = os.path.join(RACINE, 'modeles', 'lettre_officielle_RAD.gabarit.docx')
FRAGMENTS = os.path.join(RACINE, 'modeles', 'fragments')

DEFAUTS = {
    'DATE': '',
    'NUMERO': '    ',                      # laisse en blanc pour la main
    'ANNEE': '',                           # deux chiffres, deduit de l'annee courante
    'DESTINATAIRE': 'Au Dir AdmLog',
    'OBJET': '',
    'OUVERTURE': 'Honneur de vous saluer et vous transmettre ce dont l’objet repris en marge.',
    'CLOTURE': 'Profonds respects.',
    'SIGNATAIRE': 'MUFALME BULENDA Josué',
    'FONCTION': 'Chef Div Numérique',
}
CHAMPS = set(DEFAUTS)


# --------------------------------------------------------------------------- #
# lecture de l'entree
# --------------------------------------------------------------------------- #
def lire_entree(chemin):
    brut = open(chemin, encoding='utf8').read().replace('\r\n', '\n')
    if '\n---' in '\n' + brut:
        entete, corps = re.split(r'\n-{3,}[ \t]*\n', '\n' + brut, maxsplit=1)
    else:
        entete, corps = '\n' + brut, ''

    champs = {}
    restes = []
    for ligne in entete.split('\n'):
        m = re.match(r'^([A-ZÉÈÀ_]+)\s*:\s*(.*)$', ligne.strip())
        if m and m.group(1) in CHAMPS:
            champs[m.group(1)] = m.group(2).strip()
        elif ligne.strip():
            restes.append(ligne.strip())
    if restes and not corps:
        # pas de separateur --- : tout ce qui n'est pas un champ devient le corps
        corps = '\n\n'.join(restes)
    elif restes:
        raise SystemExit('Lignes non reconnues avant le separateur --- :\n  '
                         + '\n  '.join(restes))

    paragraphes = []
    for bloc in re.split(r'\n\s*\n', corps):
        # dans un meme bloc, chaque ligne commencant par "- " est une puce a part ;
        # les autres lignes consecutives forment un seul paragraphe
        tampon = []
        for ligne in bloc.split('\n'):
            ligne = ligne.strip()
            if not ligne:
                continue
            if ligne.startswith('- '):
                if tampon:
                    paragraphes.append(' '.join(tampon))
                    tampon = []
                paragraphes.append(ligne)
            else:
                tampon.append(ligne)
        if tampon:
            paragraphes.append(' '.join(tampon))

    if not champs.get('OBJET'):
        raise SystemExit('Le champ OBJET est obligatoire.')
    if not paragraphes:
        raise SystemExit('Le corps de la lettre est vide.')
    return champs, paragraphes


# --------------------------------------------------------------------------- #
# typographie francaise et balisage
# --------------------------------------------------------------------------- #
def typo(texte):
    t = texte.replace("'", '’').replace('...', '…')
    t = re.sub(r'[ \t]*\n[ \t]*', ' ', t)
    t = re.sub(r'[ \t]{2,}', ' ', t).strip()
    t = re.sub(r'[  ]*([;!?])', ' \\1', t)
    t = re.sub(r'[  ]*:(\s|$)', ' :\\1', t)
    t = re.sub(r'«[  ]*', '« ', t)
    t = re.sub(r'[  ]*»', ' »', t)
    return t


def echapper(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def segments(texte):
    """Decoupe le texte en (fragment, gras, souligne) selon **...** et __...__."""
    out = []
    for bloc, gras in _alterner(texte, r'\*\*'):
        for frag, soul in _alterner(bloc, r'__'):
            if frag:
                out.append((frag, gras, soul))
    return out or [(texte, False, False)]


def _alterner(texte, marque):
    morceaux = re.split(marque, texte)
    if len(morceaux) % 2 == 0:          # marque non fermee : on ne balise rien
        return [(texte, False)]
    return [(m, i % 2 == 1) for i, m in enumerate(morceaux)]


def rpr_avec(rpr, gras, souligne):
    """Insere <w:b/> et <w:u/> dans un rPr en respectant l'ordre du schema."""
    r = rpr
    if gras and '<w:b/>' not in r:
        r = re.sub(r'(<w:rFonts\b[^>]*/>)', r'\1<w:b/><w:bCs/>', r, count=1)
    if souligne and '<w:u ' not in r:
        ancre = re.search(r'<w:szCs\b[^>]*/>|<w:sz\b[^>]*/>', r)
        pose = '<w:u w:val="single"/>'
        r = r[:ancre.end()] + pose + r[ancre.end():] if ancre else \
            r.replace('</w:rPr>', pose + '</w:rPr>')
    return r


def runs(texte, rpr):
    out = []
    for frag, gras, soul in segments(typo(texte)):
        out.append('<w:r>' + rpr_avec(rpr, gras, soul)
                   + '<w:t xml:space="preserve">' + echapper(frag) + '</w:t></w:r>')
    return ''.join(out)


# --------------------------------------------------------------------------- #
# construction du corps
# --------------------------------------------------------------------------- #
def frag(nom):
    return open(os.path.join(FRAGMENTS, nom), encoding='utf8').read()


def puce(sk_par, rpr, texte):
    """Paragraphe a puce : numId 1 (tiret) et retrait subordonne."""
    p = sk_par.replace('<w:numId w:val="2"/>', '<w:numId w:val="1"/>')
    # dans un pPr, <w:ind> vient apres <w:spacing> (ordre impose par le schema)
    p = re.sub(r'(<w:spacing\b[^>]*/>)', r'\1<w:ind w:left="1440" w:hanging="360"/>',
               p, count=1)
    return p.replace('{{RUNS}}', runs(texte, rpr))


def construire_corps(champs, paragraphes):
    sk_ouv, rpr_ouv = frag('ouverture.xml'), frag('ouverture.rpr.xml')
    sk_par, rpr_par = frag('paragraphe.xml'), frag('paragraphe.rpr.xml')
    espace = frag('espace.xml')

    blocs = []
    separe = True            # un separateur a-t-il deja ete pose ?
    ouverture = champs.get('OUVERTURE', DEFAUTS['OUVERTURE'])
    if ouverture.lower() not in ('aucune', 'aucun', 'non', ''):
        blocs.append(sk_ouv.replace('{{RUNS}}', runs(ouverture, rpr_ouv)))
        # le modele resserre le separateur qui suit la formule d'ouverture
        blocs.append(frag('espace_ouverture.xml'))

    precedent_puce = False
    for p in paragraphes:
        est_puce = p.startswith('- ')
        if blocs and not separe and not (est_puce and precedent_puce):
            blocs.append(espace)
        separe = False
        blocs.append(puce(sk_par, rpr_par, p[2:]) if est_puce
                     else sk_par.replace('{{RUNS}}', runs(p, rpr_par)))
        precedent_puce = est_puce

    cloture = champs.get('CLOTURE', DEFAUTS['CLOTURE'])
    if cloture.lower() not in ('aucune', 'aucun', 'non', ''):
        blocs.append(espace)
        blocs.append(sk_par.replace('{{RUNS}}', runs(cloture, rpr_par)))
    return ''.join(blocs)


# --------------------------------------------------------------------------- #
# generation
# --------------------------------------------------------------------------- #
def generer(champs, paragraphes, sortie):
    zin = zipfile.ZipFile(GABARIT)
    xml = zin.read('word/document.xml').decode('utf8')

    v = dict(DEFAUTS)
    v.update({k: val for k, val in champs.items() if val != ''})
    if not v['ANNEE']:
        v['ANNEE'] = datetime.date.today().strftime('%y')
    if not v['NUMERO']:
        v['NUMERO'] = '    '

    # le corps remplace le paragraphe porteur de {{CORPS}}, en entier
    corps = construire_corps(champs, paragraphes)
    cible = next(s for s in scan.top_paragraphs(xml) if '{{CORPS}}' in xml[s[0]:s[1]])
    xml = xml[:cible[0]] + corps + xml[cible[1]:]

    for jeton in ('DATE', 'NUMERO', 'ANNEE', 'DESTINATAIRE', 'OBJET',
                  'SIGNATAIRE', 'FONCTION'):
        texte = v[jeton] if jeton in ('NUMERO', 'ANNEE') else typo(v[jeton])
        xml = xml.replace('{{%s}}' % jeton, echapper(texte))

    restants = re.findall(r'\{\{[A-Z]+\}\}', xml)
    if restants:
        raise SystemExit('Jetons non substitues : %s' % restants)

    if os.path.exists(sortie):
        os.remove(sortie)
    zout = zipfile.ZipFile(sortie, 'w', zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == 'word/document.xml':
            data = xml.encode('utf8')
        zout.writestr(item, data)
    zout.close()
    zin.close()
    return xml


def apercu(xml):
    """Texte de la lettre, avec la numerotation automatique reconstituee."""
    def dechapper(t):
        return (t.replace('&lt;', '<').replace('&gt;', '>')
                 .replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&'))

    lignes = []
    n = 0
    for a, b in scan.top_paragraphs(xml):
        f = xml[a:b]
        t = dechapper(scan.text_of(f))
        numerote = '<w:numId w:val="2"/>' in f
        pucee = '<w:numId w:val="1"/>' in f
        if numerote:
            n += 1
            lignes.append('%d. %s' % (n, t.strip()))
        elif pucee:
            lignes.append('     - %s' % t.strip())
        elif t.strip():
            lignes.append(re.sub(r'[ \t]{2,}', '  ', t))
    return '\n'.join(lignes)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('entree', help='fichier .txt decrivant la lettre')
    ap.add_argument('-o', '--sortie', help='chemin du .docx a produire')
    ap.add_argument('--texte', action='store_true',
                    help='affiche le texte final pour relecture')
    a = ap.parse_args()

    champs, paragraphes = lire_entree(a.entree)
    sortie = a.sortie or os.path.splitext(a.entree)[0] + '.docx'
    xml = generer(champs, paragraphes, sortie)
    print('Lettre generee : %s' % sortie)
    if a.texte:
        print('-' * 72)
        print(apercu(xml))
        print('-' * 72)


if __name__ == '__main__':
    main()
