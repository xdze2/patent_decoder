from flask import Flask
from flask import render_template, abort, redirect, url_for

# from flask_frozen import relative_url_for as url_for

import pickle

# from tools_for_webapp import *

# -- How to run Flask: --
# $ export FLASK_DEBUG=1
# $ FLASK_APP=web_app.py flask run


app = Flask(__name__)

app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_IGNORE_404_NOT_FOUND'] = True

#  --- during app creation ---'
# https://stackoverflow.com/a/28545503/8069403

# app.add_template_global(url_for)
# app.context_processor(lambda: {'url_for': url_for})

import os


""" Config
"""

FIGURESDIR = 'figures_extracted/'
THUMBNAILSDIR = 'thumbnails/'

""" Tools
"""

def get_thumbfig_path( patentnum ):
    """ donne l'url de la miniature pour un brevet (image n°0)
    """
    thumbname = patentnum + '-thumbnail.png'
    thumbpath = THUMBNAILSDIR + thumbname

    if os.path.isfile('static/'+thumbpath):
        path = thumbpath
    else:
        path = ''

    return path

def get_info_for_citation( patent ):

    inventorstr = lambda inventorList: ', '.join([a['name_formatted'] for a in inventorList ])

    info = { 'year':patent['year'], 'title':patent['title'],
            'inventor': inventorstr( patent['inventor'] ),
            'thumbnail':get_thumbfig_path(patent['patent_number']), 'patentnumber':patent['patent_number'] }

    return info

def get_figlist( figures ):
    """ donne l'url et d'autre info pour toutes les figures
        d'un brevet
    """
    w_fig0 = figures[0]['width']

    scale = lambda w: min( 100, 100*w/w_fig0 )

    figlist = [ {'path':FIGURESDIR+figinfo['filename'],
            'scale':scale( figinfo['width'] ) } for figinfo in figures ]

    return figlist





def insertbefore( i, string, text ):
    """ insert 'string' in 'text' before the position 'i'
    """
    newtext = list(text)
    newtext.insert( i, string )
    newtext = ''.join( newtext )
    return newtext

def insertseveralbefore( severalstrings, text ):
    """ insert plusieurs chaine de caractères aux positions i :
        severalstrings = [ (i, str), (i,str), ... ]
    """
    offset = 0
    for i, string in severalstrings:
        text = insertbefore( offset+i, string, text )
        offset = offset + len( string )

    return text

def highlightdescription( description, raw_legend ):
    """ Ajoute les balises HTML dans la description
        correspondant à la legende

        !!! HTML inside :( ... use filter ?
    """
    tobeinserted = []
    for line in raw_legend:
        end =  line['position'][1]
        start =  line['position'][0] - len(line['label']) - 2

        start_tag = '<span class="highlightfromlegend legenditem%s">' % line['numero']
        end_tag = '</span>'

        tobeinserted.append( (start, start_tag) )
        tobeinserted.append( (end, end_tag) )

    htmldescription = insertseveralbefore( tobeinserted, description )
    return htmldescription


""" Chargement des données
"""

PATENTINFO = pickle.load( open( "data/patent_infos.pickle", "rb" ) )

SORTEDPATENTS = sorted( PATENTINFO.items() , key=lambda x:x[1]['date_str'] )

""" Group patent by years/decenie
    for patent list
"""
# init
getdecade = lambda y: y - y%10

years = sorted( { getdecade( patent['year'] ) for patent in PATENTINFO.values() } )
PATENTLISTBYYEAR =   { y:[] for y in years }

# Loop
for patent in PATENTINFO.values():
    date = patent['year'], patent['month'], patent['day']
    decade = getdecade( date[0] )
    PATENTLISTBYYEAR[decade].append( {'patent_number': patent['patent_number'], 'date':date} )

# Sort  in each groups
for year, patents in PATENTLISTBYYEAR.items():
    PATENTLISTBYYEAR[year] = sorted( patents, key=lambda x:x['date']  )

PATENTLISTBYYEAR = sorted( PATENTLISTBYYEAR.items(), key= lambda x:x[0]  )


""" ---  Patent List Page ---
"""
@app.route("/")
def hello():
    return redirect(url_for('patentlist'))


@app.route('/list.html')
def patentlist():
    # liste l'ensemble des brevets avec les liens vers /figs/
    data = []
    for year, patentsoftheyear in PATENTLISTBYYEAR:
        patents_resume = []
        for patentinfo in patentsoftheyear:
            resume = get_info_for_citation( PATENTINFO[patentinfo['patent_number']] )
            patents_resume.append( resume )

        data.append( {'year':year, 'patents':patents_resume} )


    return render_template( 'patentlist.html.j2', byyear=data   )


##, 200, {'Content-Type': 'text/html; charset=utf-8'}


""" ---  Patent View Page ---
"""

@app.route('/view/<string:patent_id>.html')
def patentinfo(patent_id):

    # affiche les infos pour un brevet

    if patent_id not in PATENTINFO:
        return abort(404)
    else:
        data = PATENTINFO[ patent_id ]

    citedinfo = [ get_info_for_citation( PATENTINFO[patentnum] ) for patentnum  in data['cited']  ]
    citedbyinfo = [ get_info_for_citation( PATENTINFO[patentnum] ) for patentnum  in data['citedby']  ]

    figlist = get_figlist( data['figures'] ) if data['figures'] else []

    descriptionhtml = highlightdescription( data['description'], data['raw_legend'] )

    return render_template( 'patentview.html.j2', data=data, figures=figlist,
                            citedinfo=citedinfo, citedbyinfo=citedbyinfo,
                            descriptionhtml=descriptionhtml )
