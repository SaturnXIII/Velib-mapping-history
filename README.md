## Présentation :
Mon projet consiste à utiliser les données d’un compte Vélib’ pour produire des statistiques et des cartes interactives avec les tracés des endroits où les vélos sont passés. L’idée est de proposer un historique graphique des trajets effectués.
```
__     __   _ _ _     _ 
\ \   / /__| (_) |__ ( )
 \ \ / / _ \ | | '_ \|/ 
  \ V /  __/ | | |_) |  
   \_/ \___|_|_|_.__/   
                        
Votre carte velib' est disponible dans le dossier output ✨
```
## Fonctionement : 
Il faut dans un premier temps récupérer les historiques de trajets liés à un compte. Sur cette étape, je ne peux pas vous aider directement. Je peux simplement vous dire qu’il est possible de les obtenir via l’API interne de Vélib’. Je ne vous incite pas à le faire, car cela est illégal et non éthique. Ce projet a uniquement été réalisé dans un but éducatif.
Une fois les historiques récupérés, j’enregistre les coordonnées des stations de départ et d’arrivée grâce à l’API publique de Vélib’. Ensuite, je génère des itinéraires entre ces points. Bien sûr, ces trajets ne sont pas exacts, car nous ne connaissons que les stations de départ et d’arrivée — mais c’est la meilleure estimation possible avec les données disponibles.
Enfin, je produis une carte interactive en HTML… et voilà !
### 
## Utilisation :

⚠️ Avant tout, il faut télécharger dans le dossier ressources :
Les quartier a telecharger en .geojson : https://opendata.paris.fr/explore/dataset/quartier_paris/export/?disjunctive.c_ar
Les emplacements des stations velib en csv : https://opendata.paris.fr/explore/dataset/velib-emplacement-des-stations/export/
### Automatique :

1. Récupérer les données des trajets.
2. Les enregistrer dans un fichier texte : api/data.txt.
3. Lancer le script : app.sh.
4. Attendre environ une heure, puis récupérer les résultats dans le dossier output.


### Manuel :
### De requêtes à localisations :
Lancer le script analyze.py :
```python3 analyze.py
[11] Lancement : python3 saver.py 15308712 100921894
🚲 Station de départ : Jules Vallès - Charonne
🏁 Station d'arrivée : Léon Frot - Charonne
✅ Coordonnées ajoutées à coordonnees.csv
Trajets traités : 10/1951 (0.5%)
```




## Création des itinéraires :
coordonnees.csv → trajects.geojson
Script à utiliser : road.py
```python3 road.py
📥 Chargement des données de trajets...
✅ 2 trajets chargés.
📂 Chargement du graphe cyclable depuis le fichier local...
2025-06-04 12:37:59 Converting node, edge, and graph-level attribute data types
2025-06-04 12:38:03 Loaded graph with 86482 nodes and 191184 edges from 'paris_bike_10km.graphml'
2025-06-04 12:38:08 Created nodes GeoDataFrame from graph
2025-06-04 12:38:08 Projected GeoDataFrame to 'EPSG:32631 / WGS 84 / UTM zone 31N'
2025-06-04 12:38:10 Created edges GeoDataFrame from graph
2025-06-04 12:38:10 Projected GeoDataFrame to 'EPSG:32631 / WGS 84 / UTM zone 31N'
2025-06-04 12:38:16 Created graph from node/edge GeoDataFrames
2025-06-04 12:38:16 Projected graph with 86482 nodes and 191184 edges
🚴 Calcul des itinéraires vélo...
2025-06-04 12:38:16 Created nodes GeoDataFrame from graph
2025-06-04 12:38:17 Created nodes GeoDataFrame from graph
2025-06-04 12:38:17 Created nodes GeoDataFrame from graph
2025-06-04 12:38:18 Created nodes GeoDataFrame from graph
✅ 149 segments utilisés au total.
🧱 Création des géométries pour GeoJSON...
💾 Sauvegarde dans 'trajects.geojson'...
✅ Fichier GeoJSON généré avec 149 lignes.
```


## Export des itinéraires en carte interactive :
trajects.geojson → carte_pastel_interactive.html
Script à lancer : web-maker.py
```python3 web-maker.py
✅ Carte enregistrée dans 'carte_interactive.html'
```

