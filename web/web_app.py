from flask import Flask
from flask import render_template, abort, url_for

import pickle

# How to run Flask:
# $ export FLASK_DEBUG=1
# $ FLASK_APP=web_app.py flask run


app = Flask(__name__)

import os

@app.route("/")
def hello():
    return "Hello World!"


@app.route('/hello')
def helloyou():
    return 'Hello you'

FIGURESDIR = 'figures_extracted/'

PATENTINFO = pickle.load( open( "data/patent_infos.pickle", "rb" ) )

SORTEDPATENTS = sorted( PATENTINFO.items() , key=lambda x:x[1]['date_str'] )

@app.route('/list')
def patentlist():
    # liste l'ensemble des brevets avec les liens vers /figs/

    data = [ {'url':'/view/'+patnumber,
              'patentnumber':patnumber,
              'nbre_figures':len( infos['figures']) }
               for patnumber, infos in SORTEDPATENTS ]

    return render_template( 'patentlist.html.j2', patentlist=data   )


@app.route('/view/<string:patent_id>')
def patentinfo(patent_id):
    # affiche les infos pour un brevet

    if patent_id not in PATENTINFO:
        return abort(404)
    else:
        data = PATENTINFO[ patent_id ]

    figlist = [ url_for( 'static', filename=FIGURESDIR+figinfo['filename'])
                for figinfo in data['figures'] ]

    return render_template( 'patentview.html.j2', data=data, figures=figlist   )




def patentid_from_figname( figname ):
    return figname.split('-')[0]

FIGURESLIST =  os.listdir( 'static/'+FIGURESDIR )

def find_figures( patent_number ):
    # Retrouve les figures
    #   retourne l'url static
    patentfiglist = [ url_for('static', filename=FIGURESDIR+figname )
                        for figname in FIGURESLIST
                        if patentid_from_figname( figname ) == patent_number  ]
    # sort ?
    return  patentfiglist
