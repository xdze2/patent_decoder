# Patent Decoder

Projet d'interface pour visualiser des brevets avec un point de vue technique, c'est-à-dire avec les figures, la légende et le texte de description technique. Pas de revendications, date de priorité... etc


Les données sont obtenues entre autre avec [google BigQuery et ses Patents Public Data](https://console.cloud.google.com/launcher/partners/patents-public-data). L'interface web est réalisée avec Flask, puis Flask-frozen.


Un des gros aspect du projet est d'**extraire les images** depuis les pdf des brevets. Ceci est réalisé avec la libraire `ndimage` de scipy. Une certaine succesion d'opérations de [dilatation et d'érosion](https://fr.wikipedia.org/wiki/Morphologie_math%C3%A9matique) permet de détecter la présence d'une figure (à contrario du texte) puis de trouver la zone où elle s'étend. L'astuce est de chercher les zones encloses larges.


**L'extraction de la légende** se base sur une série d'expression régulière cherchant les numéros isolés, puis un choix est fait pour sélectionner un unique label : pour chaque mot en partant de la fin, est selectionné celui le plus présent, si exaequo alors arrêt.




## La suite

* utiliser [open patent service](http://www.epo.org/searching-for-patents/technical/espacenet/ops.html#tab-1) comme source de données
* Traiter le texte de la description avant la recherche de la légende, afin de supprimer quelques erreurs.
* Gérer les numérotations avec des lettres
* OCR des images : numéro sur les figures, et (identification du numéro de la figure ?)
