
# coding: utf-8

# # Extraire la legende depuis la description

# In[1]:


import regex   # permet overlapping matching
import copy


# In[442]:


def print_legend( legend ):
    sortfun = lambda x: ( x['number'] , len(x['position']), x['label'][::-1] )
    legendsorted = sorted( legend, key=sortfun  )

    current_number = legendsorted[0]['number']
    for match in legendsorted:
        if current_number != match['number']:
            print('     --')
            current_number = match['number']

        n_merged = len(match['position'])
        n_merged_str = '  ' if n_merged==1 else '(%i)'%n_merged
        print( '{label:>42} {number:>4}  {n}  {context:>35}'.format( **match, n=n_merged_str) )


# In[2]:


def fullTextTrimming( description ):
    """ Travail sur le texte entier
        en gardant le nombre de caractère constant
    """
    description = description.replace('\n', ' ')
    description = description.lower()

    description = regex.sub('[()]',' ', description) # remove parentheses
    
    # description = regex.sub('\s+',' ', description) # remove multiple space

    # patent number XX
    # patent_number_pattern = r'(\d{1, 4}[,-])?\d{3, 8}[,-]\d{3, 8}'
    # description = regex.sub(patent_number_pattern, '', description  )

    # remove non-AASII caracters
    description = regex.sub(r'[^\x00-\x7F]', ' ', description)

    return description


# In[3]:


def findAllCandidates( description ):
    """ Recherche  les chiffres isolés pouvant correspondre à un numéro de légende

        par exemple   " 4, 5 and 6 ", ou " 6 and 7 ", " 6, 7 "

        retourne une legend : liste avec les infos pour chaque 'match'
    """

    pattern =  r' (\d{1,3}(( ?, ?| and | or )\d{1,3})*)[^a-z0-9\-]'

    # Explication:
    # la forme générale est E(SE) avec Element  Separator
    # et le séparateur est une virgule ou and ou or

    allmatches = list( regex.finditer(pattern, description) )
    splitpattern = regex.compile(r'[^\d]+')

    legend = []
    for m in allmatches:
        capture = m.group(1)
        numbers = splitpattern.split( capture )
        start = m.start()

        label = description[ max(0, m.start()-40 ): m.start() ]  # to prevent overlapping
        label = label.strip(' ')  # cas avec plusieurs espace consécutifs

        context = description[ max(0, m.start()-16 ): min( len(description), m.end()+10 ) ]  # to debug

        for n in numbers:
            item = {'number':int(n), 'label':label, 'position':[m.span(1)], 'context':context}
            legend.append( item )

    return legend


# In[4]:


def disqualify( legend, pattern, n=-1 ):
    for i, row in enumerate( legend ):
        if pattern.search( row['label'] ):
            legend[ i ]['number'] = n

KEYWORDS = ['january', 'february', 'march', 'april', 'may', 'june',            'july', 'august', 'september', 'october', 'november', 'december',            'fig', 'figure', 'figures', 'claim', 'claims', 'at', 'and',            'numeral', 'embodiment', 'invention', 'part']

KEYWORDS.extend( ['the', 'a', 'an', 'these', 'their', 'when', 'with', 'by', 'this',                    'have', 'having', 'has', 'is', 'are', 'over', 'its', 'of said', 'and', 'as',                   'of', 'in', 'to', 'but', 'another', 'through', 'on'] )

def firstScreening( legend ):
    """ Premier filtrage en regardant comment se termine le label,
        Critères éliminants:

            - ne se termine pas par une lettre (Typiquement Fig. 5)
            - se termine par un des mots clés ('claim') ou un mot commun

        change le numéro pour 998 ou 999..
    """
    newlegend = copy.deepcopy(legend) # copy (pour ne pas ecrasser Legend)

    pattern = regex.compile( r'[^a-z]$', regex.I )
    disqualify( newlegend, pattern )


    pattern = regex.compile( r'\W(%s)$' % '|'.join(KEYWORDS), regex.I )
    disqualify( newlegend, pattern )

    return newlegend


# In[5]:


def cut_legend_using_pattern( legend, pattern ):
    for i, row in enumerate( legend ):
        label = row['label']

        match = pattern.search(label)

        if match:
            newlabel = match.group(2)
            legend[i]['label'] = newlabel

SMALL_WORDS = ['the', 'a', 'an', 'these', 'their', 'when', 'with', 'by', 'this', 'that',                'have', 'having', 'has', 'is', 'are', 'should', 'over', 'its', 'of said', 'and', 'as',               'of', 'in', 'to', 'at',  'but', 'another', 'through', 'on', 'same', 'from',               'include', 'includes', 'beyond', 'between']


# In[6]:


def cutLabels( legend ):
    """ coupe les labels sur certain mots commun ('the', 'a'... etc)
        et sur certains caractères spéciaux (. , ;)
    """
    newlegend = copy.deepcopy(legend) # copy (pour ne pas ecrasser Legend)

    pattern_small_words = regex.compile( r'^.* (%s) (.+)$' % '|'.join(SMALL_WORDS), regex.I )
    cut_legend_using_pattern( newlegend, pattern_small_words )

    pattern = regex.compile( '^.*([\.,;] )(.+)$' )
    cut_legend_using_pattern( newlegend, pattern )

    return newlegend


# ### Merge : regroupe les candidats ayant un label identique
#
# Rq: utile pour le dev. mais pas pour l'identification

# In[7]:


def get_positions( label, candidats ):
    positions = []
    for item in candidats:
        if item['label']==label:
            positions.extend( item['position'] )
    return positions

def get_context( label, candidats ):
    items = [ item for item in candidats if item['label']==label ]

    return items[0]['context']

def merge( legend ):
    # merge identical label

    numbers_unique = { item['number'] for item in legend  } # set

    new_legend = []
    for n in numbers_unique:

        candidats = [ line for line in legend if line['number']==n ]

        labels_unique = { item['label'] for item in candidats  }

        new_candidats = [ { 'number':n, 'label':label_u,                           'position':get_positions(label_u, candidats), 'context':get_context(label_u, candidats) }
                          for label_u in labels_unique ]

        new_legend.extend( new_candidats )

    return new_legend


# ## Identification du meilleur candidats

# In[8]:


def candidates_for_onenumber( legend, i ):
    candidates = [ line.copy() for line in legend if line['number'] == i ]

    for line in candidates:
        line['reversed'] = line['label'].split(' ')[::-1]
        line['weight'] = len( line['position'] )

    return candidates


# In[9]:


def increment_dico( dico, key, value ):
    if key in dico:
        dico[key] += value
    else:
        dico[key] = value

def append_dico( dico, key, value ):
    if key in dico:
        dico[key].append( value )
    else:
        dico[key] = [value]

def who_are_the_winners( scoreboard ):
    scoreMax = max( scoreboard.values() )
    winners = [ sb[0] for sb in scoreboard.items() if sb[1] == scoreMax ]
    return winners


# In[461]:


def choose_best_label( remainingcandidates ):
    """ Choisi un candidat gagnant unique

        choisi le label mot par mot, en partant de la fin :
            - si un mot apparait plus souvent que tout les autres, alors il est choisi
            - si plusieurs mots apparaissent aussi souvent, alors le label est coupé ici
    """
    N = len( remainingcandidates )

    if N == 1:
        return remainingcandidates[0]['label']

    previouschoice=[]
    for i in range(20):
        current_indice = len(previouschoice)

        scoreboard = {}
        nextword2candidates ={}
        for c in remainingcandidates:
            if current_indice < len( c['reversed'] ):
                next_word = c['reversed'][ current_indice ]
            else:
                next_word = ''

            append_dico( nextword2candidates, next_word, c )
            increment_dico( scoreboard, next_word, c['weight'] )

            #print(next_word, c['weight'])

        #print( 'scoreboard: ', scoreboard )
        winners = who_are_the_winners( scoreboard )
        #print( 'winners:', winners )
        if len(winners) == 1 and winners[0]:
            choice = winners[0]
            remainingcandidates = nextword2candidates[choice]
            previouschoice.append( choice )
            #print(' ')

        else: # exaequo ou fin -> stop
            selectedlabel = ' '.join( previouschoice[::-1] )
            #print( selectedlabel )
            break

    return selectedlabel


# In[10]:


def getUniqueLabel(legend):
    allnumbers = sorted( { c['number'] for c in legend if c['number']>0 } ) # unique et triés

    final_legend = []
    for numero in allnumbers:
        candidates = candidates_for_onenumber(legend, numero)
        thelabel = choose_best_label( candidates )

        if not thelabel: continue
        line = {'numero':numero , 'label':thelabel  }
        final_legend.append( line )

    return final_legend


# In[12]:


def findAndFilter( description ):
    description = fullTextTrimming( description )
    legend = findAllCandidates( description )
    legend = firstScreening(legend)
    legend = cutLabels(legend)

    return legend

def extract_legend( description ):
    legend = findAndFilter( description )
    final_legend = getUniqueLabel(legend)

    raw_legend = [ {'label':line['label'], 'position':line['position'][0],
            'numero':line['number']} for line in legend if line['number']>0 ]

    return final_legend, raw_legend
