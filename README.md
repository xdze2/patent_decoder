
[<img src='https://raw.githubusercontent.com/xdze2/patent_decoder/master/Screenshot-US20060180169.png' style='width:600px;' alt='screenshot'/>]( https://xdze2.github.io/nailclipper/view/US20060180169.html )


# Patent Decoder

Projet d'interface pour visualiser des brevets avec _un point de vue technique_, c'est-à-dire avec les figures, la légende et le texte de description technique. Pas de revendications ou de date de priorité... etc


Les données sont obtenues entre autres avec [google BigQuery et ses Patents Public Data](https://console.cloud.google.com/launcher/partners/patents-public-data). L'interface web est réalisée avec Flask, puis le site statique est obtenu avec Flask-Frozen.


Un des gros aspects du projet est d'**extraire les images** depuis les PDF des brevets. Ceci est réalisé avec la libraire `ndimage` de scipy. Une certaine succesion d'opérations de [dilatation et d'érosion](https://fr.wikipedia.org/wiki/Morphologie_math%C3%A9matique) permet de détecter la présence d'une figure (a contrario du texte) puis de trouver la zone où elle s'étend. L'astuce est de chercher les zones encloses larges.

<img src='https://raw.githubusercontent.com/xdze2/patent_decoder/master/illu_algoextractimg.png'  width="200"  alt='étape extraction figure'/>


**L'extraction de la légende** se base sur une série d'expressions régulières cherchant les numéros isolés, puis un choix est fait pour sélectionné un unique label : pour chaque mot en partant de la fin, est selectionné celui le plus présent, si ex aequo alors arrêt.




## La suite

* utiliser [open patent service](http://www.epo.org/searching-for-patents/technical/espacenet/ops.html#tab-1) comme source de données
* Traiter le texte de la description avant la recherche de la légende, afin de supprimer quelques erreurs.
* Gérer les numérotations avec des lettres
* OCR des images : numéro sur les figures, et identification du numéro de figure?


## Requirements
* numpy, scipy
* Wand
* Flask, Frozen-Flask
* python-magic
