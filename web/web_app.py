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
    
    
PATENTINFO = pickle.load( open( "data/patent_infos.pickle", "rb" ) )
    
SORTEDPATENTS = sorted( PATENTINFO.items() , key=lambda x:x[1]['date_str'] )

@app.route('/list')
def patentlist():
    # liste l'ensemble des brevets avec les liens vers /figs/
    
    data = [ {'url':'/view/'+patnumber,
              'patentnumber':patnumber, 
              'nbre_figures':len( find_figures( patnumber )) }
               for patnumber, infos in SORTEDPATENTS ]
               
    return render_template( 'patentlist.html', patentlist=data   )


@app.route('/view/<string:patent_id>')
def patentinfo(patent_id):
    # affiche les infos pour un brevet

    if patent_id not in PATENTINFO:
        return abort(404)
    else:
        data = PATENTINFO[ patent_id ]

    patentfiglist = find_figures( patent_id )
   
    return render_template( 'patentview.html', data=data, figures=patentfiglist   )
    
    

@app.route('/figs/<string:patent_id>')
def show_figures(patent_id):
    # affiche les figures pour un brevet

    patentfiglist = [ url_for('static', filename=FIGURESDIR+figname ) 
                        for figname in FIGURESLIST 
                        if patentid_from_figname( figname ) == patent_id  ]
     
    if len( patentfiglist ) == 0:
        return abort(404)
        
    return render_template( 'figures.html', figurl=patentfiglist   )
    
    
def patentid_from_figname( figname ):
    return figname.split('-')[0]
    

FIGURESDIR = 'figures_extracted/'
FIGURESLIST = os.listdir( 'static/'+FIGURESDIR )
   
def find_figures( patent_number ):
    # Retrouve les figures 
    #   retourne l'url static
    patentfiglist = [ url_for('static', filename=FIGURESDIR+figname ) 
                        for figname in FIGURESLIST 
                        if patentid_from_figname( figname ) == patent_number  ]
                        
    return patentfiglist
