from flask import Flask
from flask import render_template, abort, url_for

app = Flask(__name__)

import os

@app.route("/")
def hello():
    return "Hello World!"
    
    
@app.route('/hello')
def helloyou():
    return 'Hello you'
    
    
FIGURESDIR = 'figures_extracted/'
FIGURESLIST = os.listdir( 'static/'+FIGURESDIR )


@app.route('/list')
def patentlist():
    # liste l'ensemble des brevets avec les liens vers /figs/
    
    data = [ {'url':'/figs/'+patentid_from_figname( figname ),
              'patentnumber':patentid_from_figname( figname )}
               for figname in FIGURESLIST ]
    return render_template( 'patentlist.html', patentlist=data   )



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
