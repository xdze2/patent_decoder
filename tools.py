




def format_patentnumber( pubnumber ):
    """  formate le numéro de brevet, dans le style de google
    c.a.d. année + 7 digits, avec des zéro si besoin

    voir:
    https://www.cas.org/training/stneasytips/patentnumber2.html#anchor1
    https://www.uspto.gov/patents-application-process/applying-online/patent-number
    http://www.bpmlegal.com/howtopat1.html
    """
    number = pubnumber.split('-')[1]

    if len( number ) > 7:  # en vrai ==10
        number = number[0:4] + number[4:].zfill(7)

    number = 'US' + number

    return number


import re

""" ===============  Formate texte  ===============
"""

def format_name( name ):
    """ Formate le nom des inventeurs/assignees
        PRENOM I NOM ->  Prenom I. Nom
    """
    # ajoute le point pour une initiale (lettre seule)
    singleletter = re.compile( r'\b(?P<letter>[A-Z])(?!\.)\b' )
    name = singleletter.sub('\g<letter>.', name)

    # passe en minuscule sauf premiere lettre
    wordpattern = re.compile( r'\b(?P<word>\w+)\b' )
    titlefun = lambda match:  match.group('word').title()
    name = wordpattern.sub(titlefun, name)

    # JR -> Jr.
    JRpattern = re.compile( r'\b(?P<jr>JR)(?!\.)\b', re.I )
    name = JRpattern.sub('Jr.', name)

    return name

# -- test
# name = 'FRIEDMAN JR DAVID Jr. H hello B'
# tl.format_name( name )
# name

""" ===============  citations  ===============
"""

def countplusone( dico, key ):
    """ compte, dans le dictionaire dico, les occurences de la clé 'key'
    """
    if key in dico:
        dico[ key ] += 1
    else:
        dico[ key ] = 1



""" ===============  Figures  ===============
"""

fignamepattern = re.compile( r"^(US[0-9A-Z]+)-fig([0-9]+).png$" )

def nums_from_figurename( figname ):
    """ retourne le numéro de brevet
        et le numéro de la figure
        à partir du nom de fichier de la figure
        du type   US138061-fig2.png
    """
    matchs = fignamepattern.match( figname )
    fignum = matchs.group(2)
    patnum = matchs.group(1)

    return patnum, fignum


import magic

def get_imagesize( figpath ):
    """ retrouve la taille de l'image (png), sans ouvrir le fichier
        from https://stackoverflow.com/a/19035508/8069403
    """
    filebegining = magic.from_file( figpath )
    w, h = re.search('(\d+) x (\d+)', filebegining).groups()

    return int(w), int(h)



""" ===============  Legende  ===============
"""

import numpy as np

def isThereOddNumber( legend, k=2 ):
    numlist = np.array( [ line['numero'] for line in legend ] )
    thereisOddNumber = ( numlist % k ).any()
    return thereisOddNumber

def add_consecutive_field( legend ):
    """ test si les numéros sont consécutifs (sans gap)
    """
    increment = 1 if isThereOddNumber(legend) else 2
    # parce que certaines legendes sont numérotée de deux en deux...

    for i in range( len(legend)-1 ):
        n = legend[i]['numero']
        nSuivant = legend[i+1]['numero']
        if n+increment == nSuivant:
            legend[i]['consecutive'] = True
        else:
            legend[i]['consecutive'] = False

    legend[-1]['consecutive'] = True
