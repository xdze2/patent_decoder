
# coding: utf-8

# In[2]:


import requests
import pickle
import os
import time
from random import randint


# In[43]:


PDFSPATH = 'pdfs/'
DATAPATH = "../web/data/patent_infos.pickle"


# # Liste les pdfs

# In[44]:


data = pickle.load( open( DATAPATH, "rb" ) )

allpatents_list = list( data.keys() )

print('nombre de brevets: %i' %len(allpatents_list))


# In[45]:


def ispdfpresent( patentnumber ):
    pdffilename = '%s.pdf' % patentnumber
    
    if os.path.isfile( PDFSPATH + pdffilename ) :
        exist = True
    else:
        exist = False
    return exist


# In[46]:


missing_patents = [ p for p in allpatents_list if not ispdfpresent( p )  ]
print( 'nombre de brevets encore sans pdf: %i' % len(missing_patents) )


# In[47]:


get_patentnum = lambda filename : filename.strip('.pdf')

lost_pdf = [ filename for filename in os.listdir( PDFSPATH ) if get_patentnum(filename) not in data ]
print( 'nombre de fichier ne correspondant pas à un brevet : %i' % len(lost_pdf) )


# # Téléchargement

# In[36]:


session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',                         'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'})

#session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0', \
#                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'})


# see
# http://edmundmartin.com/random-user-agent-requests-python/

# In[ ]:


def query_google(patent_number):
   
    pdfname = '%s.pdf' % patent_number

    # google
    url = 'http://patentimages.storage.googleapis.com/pdfs/%s' % pdfname

    # query
    print( url, end='\r' )
    r = session.get(url)

    if r.status_code == 200:
        with open(PDFSPATH+pdfname, "wb") as file:
            file.write( r.content )
            print( 'save %s    ' % pdfname )
            sucess = True

    else:
        sucess = False
        print('\n\n\n error: %i'%r.status_code)

        
    return sucess



def query_pat2pdf(patent_number):
    
    patentsdigits = patent_number.strip('US').lower()

    truepdfname = patent_number+'.pdf'
    
    # pat2pdf
    url_search = 'http://www.pat2pdf.org/pat2pdf/foo.pl?number=%s' % patentsdigits
    url_file = 'http://www.pat2pdf.org/patents/pat%s.pdf' % patentsdigits

   
    # query 1
    print( url_search, end='\r' )
    r = session.get( url_search )
    time.sleep( 4 )
    
    if r.status_code == 200:
        # query 2
        print( url_file, end='\r' )
        r = session.get( url_file )
        
        if r.status_code == 200:
            with open(PDFSPATH + truepdfname, "wb") as file:
                file.write( r.content )
            print( 'save %s     ' % truepdfname )
            sucess = True     
        else:
            sucess = False
            print('\n\n\n error: %i '%r.status_code)
            print( url_file )
    else:
        sucess = False
        print('\n\n\n error: %i '%r.status_code)
        print( url_search )

        
    return sucess


class stoploop(Exception):
    pass


# In[52]:


# -- Loop --

print('')
print( 'il manque encore %i brevets' % len( missing_patents ) )

N_loop = input('_ Combien ? ')
if not N_loop.isdigit( ) :
    print(  N_loop )
    raise stoploop( 'abort' )
else:
    N_loop = int( N_loop )
    

source = input('_ depuis google[g] ou pat2pdf[p] ? ')
if source == 'p' :
    query = lambda patnum: query_pat2pdf(patnum)
elif source == 'g':
    query = lambda patnum: query_google(patnum)
else:
    raise stoploop( 'abort' )
    
    
for patent_number in missing_patents[:N_loop]:

    #  query
    # remarque .. vieux brevet -> google,  nouveau -> pat2pdf...
    # sep. 2000 ?  Renumbering each year   YYYYnnnnnn  vs nnnnnn  ??
    
    sucess = query(patent_number)
    #sucess = query_google(patent_number)
    
    # arret si erreur
    if not sucess:
        print('end loop : %s'%patent_number)
        break
    
    # timer
    timer = randint(10, 60)
    print( ' wait %i s... ' % timer, end='\r' )
    time.sleep( timer )
    
else:
    print( ' - done - ' )


# ### Liens
# 
# http://www.pat2pdf.org/pat2pdf/foo.pl
#     
# https://patents.google.com/    
