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

Champs reconnus (tous optionnels sauf OBJET) : OBJET, REF, DESTINATAIRE,
DESTINATAIRE2, DATE, NUMERO, ANNEE, SALUTATION, OUVERTURE, CLOTURE,
CLOTURE_NUMEROTEE, SIGNATAIRE, FONCTION. La formule d'ouverture et la formule de
politesse sont ajoutees automatiquement (voir DEFAUTS ci-dessous) ; valeur
"aucune" pour les supprimer.

Les paragraphes du corps sont separes par une ligne vide. Balisage :
    **gras**            -> gras
    __souligne__        -> souligne
    # Titre de section  -> titre en gras, hors numerotation
    * sous-point        -> numerotation en lettres a., b., c. (numId 7)
    - element           -> puce (numId 1, tiret)
Les paragraphes ordinaires sont numerotes 1., 2., 3. automatiquement par Word
(numId 2), exactement comme dans le modele d'origine. Les titres, les
sous-points et les puces sont hors de cette sequence, qui reprend donc son cours
apres eux.
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
    'DESTINATAIRE2': '',                   # 2e ligne, ex. « à Kinshasa/Gombe »
    'OBJET': '',
    'REF': '',                             # ligne « RÉF. : » sous l'objet
    'SALUTATION': '',                      # ex. « Monsieur le Directeur, »
    'OUVERTURE': 'Honneur de vous saluer et vous transmettre ce dont l’objet repris en marge.',
    'CLOTURE': 'Profonds respects.',
    'CLOTURE_NUMEROTEE': 'oui',            # « non » pour sortir la clôture de la numérotation
    'SIGNATAIRE': 'MUFALME BULENDA Josué',
    'FONCTION': 'Chef Div Numérique',
}
CHAMPS = set(DEFAUTS)
NON = ('aucune', 'aucun', 'non', '')


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
        m = re.match(r'^([A-ZÉÈÀ_0-9]+)\s*:\s*(.*)$', ligne.strip())
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


def _sans_numerotation(p):
    return re.sub(r'<w:numPr>.*?</w:numPr>', '', p, flags=re.S)


def _retrait(p, gauche, suspendu=360):
    """Pose un retrait explicite ; dans un pPr, <w:ind> vient apres <w:spacing>."""
    return re.sub(r'(<w:spacing\b[^>]*/>)',
                  r'\1<w:ind w:left="%d" w:hanging="%d"/>' % (gauche, suspendu),
                  p, count=1)


def _numero_gras(p):
    """Rend le marqueur de liste gras (il herite du rPr de la marque de paragraphe)."""
    return re.sub(r'(<w:rPr><w:rFonts\b[^>]*/>)', r'\1<w:b/><w:bCs/>', p, count=1)


def paragraphe_simple(sk_par, rpr, texte):
    """Paragraphe du corps, numerote 1., 2., 3. par Word (numId 2, comme le modele)."""
    return sk_par.replace('{{RUNS}}', runs(texte, rpr))


def titre_section(sk_par, rpr, texte):
    """Titre de section, en gras, hors numerotation."""
    p = _sans_numerotation(sk_par)
    return p.replace('{{RUNS}}', runs('**' + texte + '**', rpr))


def sous_point(sk_par, rpr, texte):
    """Sous-point a., b., c. : numId 7 (lettres minuscules), retrait subordonne."""
    p = sk_par.replace('<w:numId w:val="2"/>', '<w:numId w:val="7"/>')
    p = _numero_gras(_retrait(p, 1080))
    return p.replace('{{RUNS}}', runs(texte, rpr))


def puce(sk_par, rpr, texte):
    """Paragraphe a puce : numId 1 (tiret) et retrait subordonne."""
    p = sk_par.replace('<w:numId w:val="2"/>', '<w:numId w:val="1"/>')
    return _retrait(p, 1440).replace('{{RUNS}}', runs(texte, rpr))


def non_numerote(sk_par, rpr, texte):
    """Paragraphe du corps sorti de la numerotation (interpellation, cloture)."""
    p = _sans_numerotation(sk_par)
    return p.replace('{{RUNS}}', runs(texte, rpr))


# balisage de debut de ligne -> fabricant de paragraphe
MARQUES = (
    ('# ', titre_section),
    ('* ', sous_point),
    ('- ', puce),
)


def construire_corps(champs, paragraphes):
    sk_ouv, rpr_ouv = frag('ouverture.xml'), frag('ouverture.rpr.xml')
    sk_par, rpr_par = frag('paragraphe.xml'), frag('paragraphe.rpr.xml')
    espace = frag('espace.xml')

    blocs = []
    separe = True            # un separateur a-t-il deja ete pose ?

    salutation = champs.get('SALUTATION', DEFAUTS['SALUTATION'])
    if salutation.lower() not in NON:
        blocs.append(non_numerote(sk_par, rpr_par, salutation))
        separe = False

    ouverture = champs.get('OUVERTURE', DEFAUTS['OUVERTURE'])
    if ouverture.lower() not in NON:
        if not separe:
            blocs.append(espace)
        blocs.append(sk_ouv.replace('{{RUNS}}', runs(ouverture, rpr_ouv)))
        # le modele resserre le separateur qui suit la formule d'ouverture
        blocs.append(frag('espace_ouverture.xml'))
        separe = True

    marque_precedente = None
    for p in paragraphes:
        marque = next((m for m, _ in MARQUES if p.startswith(m)), None)
        fabrique = dict(MARQUES).get(marque, paragraphe_simple)
        # pas de ligne vide entre deux elements consecutifs d'une meme liste
        colle = marque in ('* ', '- ') and marque == marque_precedente
        if blocs and not separe and not colle:
            blocs.append(espace)
        separe = False
        blocs.append(fabrique(sk_par, rpr_par, p[len(marque):] if marque else p))
        marque_precedente = marque

    cloture = champs.get('CLOTURE', DEFAUTS['CLOTURE'])
    if cloture.lower() not in NON:
        blocs.append(espace)
        numerotee = champs.get('CLOTURE_NUMEROTEE',
                               DEFAUTS['CLOTURE_NUMEROTEE']).lower() not in NON
        blocs.append((paragraphe_simple if numerotee else non_numerote)
                     (sk_par, rpr_par, cloture))
    return ''.join(blocs)


def ligne_reference(texte):
    """Ligne « RÉF. : … » calquee sur le paragraphe OBJET (label gras, contenu normal)."""
    label = frag('objet.label.rpr.xml')
    corps = frag('objet.texte.rpr.xml').replace('<w:b/>', '').replace('<w:bCs/>', '')
    return frag('objet.xml').replace(
        '{{RUNS}}',
        '<w:r>' + label + '<w:t xml:space="preserve">RÉF. : </w:t></w:r>'
        + runs(texte, corps))


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

    # ligne « RÉF. : … » inseree juste apres le paragraphe OBJET
    if v['REF']:
        objet = next(s for s in scan.top_paragraphs(xml) if '{{OBJET}}' in xml[s[0]:s[1]])
        xml = xml[:objet[1]] + ligne_reference(v['REF']) + xml[objet[1]:]

    for jeton in ('DATE', 'NUMERO', 'ANNEE', 'DESTINATAIRE', 'DESTINATAIRE2', 'OBJET',
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
    n = lettre = 0
    for a, b in scan.top_paragraphs(xml):
        f = xml[a:b]
        t = dechapper(scan.text_of(f)).strip()
        if '<w:numId w:val="2"/>' in f:
            n += 1
            lignes.append('%d.  %s' % (n, t))
        elif '<w:numId w:val="7"/>' in f:
            lignes.append('    %s.  %s' % (chr(ord('a') + lettre), t))
            lettre += 1
        elif '<w:numId w:val="1"/>' in f:
            lignes.append('       -  %s' % t)
        elif t:
            lignes.append(re.sub(r'[ \t]{2,}', '  ', dechapper(scan.text_of(f))))
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
