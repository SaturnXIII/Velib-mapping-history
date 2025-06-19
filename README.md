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






<div style="display: flex; flex-wrap: wrap; justify-content: space-between;">
  <img src="https://github.com/user-attachments/assets/71b1f1df-45f1-4cdd-a49f-1c11e4a23cdf"  style="width: 48%; margin-bottom: 10px;">
  <img src="https://github.com/user-attachments/assets/cabb9f6c-46ac-4e42-a7a1-1d622720b204" style="width: 48%; margin-bottom: 10px;">
</div>
<div style="display: flex; flex-wrap: wrap; justify-content: space-between;">
  <img src="https://github.com/user-attachments/assets/efac3058-5090-445d-b84a-94c1c53075ee"  style="width: 48%; margin-bottom: 10px;">
  <img src="https://github.com/user-attachments/assets/8ecd5b62-39ad-4875-b7d5-0d5b00f4721c" style="width: 48%; margin-bottom: 10px;">
  <img src="https://github.com/user-attachments/assets/21636774-8def-49cb-9ce0-1def64750e13"  style="width: 48%; margin-bottom: 10px;">

</div>

## Fonctionement : 
Il faut dans un premier temps récupérer les historiques de trajets liés à un compte. 
Une fois les historiques récupérés, j’enregistre les coordonnées des stations de départ et d’arrivée grâce à l’API publique de Vélib’. Ensuite, je génère des itinéraires entre ces points. Bien sûr, ces trajets ne sont pas exacts, car nous ne connaissons que les stations de départ et d’arrivée — mais c’est la meilleure estimation possible avec les données disponibles.
Enfin, je produis une carte interactive en HTML… et voilà !
### 
## Utilisation :
<br>

⚠️ Avant tout, il faut télécharger dans le dossier ressources :
<br>
Les quartier a telecharger en .geojson : https://opendata.paris.fr/explore/dataset/quartier_paris/export/?disjunctive.c_ar et renommer en quartiers.geojson
<br>
Les emplacements des stations velib en csv : https://opendata.paris.fr/explore/dataset/velib-emplacement-des-stations/export/
### Automatique :
(Script pour Linux)
1. Récupérer les données des trajets.
   <br> (Merci à : https://github.com/lecfab/velibrairie/blob/main/velibrairie.js pour son inspiration).
   - Copie le contenu du fichier api/browser.js
   - Ouvre ton navigateur préféré et connecte-toi sur le site velib-metropole.fr
   - Appuie sur F12 et colle le code dans la console. Si tout se passe bien, un fichier data.txt va être téléchargé.
   - Déplace data.txt dans le dossier api : api/data.txt
 
2. Lancer le script : app.sh.
3. Attendre environ une heure, puis récupérer les résultats dans le dossier output.


## Manuel :

### Récupérer les données des trajets.
   <br> (Merci à : https://github.com/lecfab/velibrairie/blob/main/velibrairie.js pour son inspiration).
   - Copie le contenu du fichier api/browser.js
   - Ouvre ton navigateur préféré et connecte-toi sur le site velib-metropole.fr
   - Appuie sur F12 et colle le code dans la console. Si tout se passe bien, un fichier data.txt va être téléchargé.
   - Déplace data.txt dans le dossier api : api/data.txt
     
### De requêtes à localisations :
Lancer le script analyze.py :
```python3 analyze.py
[11] Lancement : python3 saver.py 15308712 100921894
🚲 Station de départ : Jules Vallès - Charonne
🏁 Station d'arrivée : Léon Frot - Charonne
✅ Coordonnées ajoutées à coordonnees.csv
Trajets traités : 10/1951 (0.5%)
```




### Création des itinéraires :
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


### Export des itinéraires en carte interactive :
trajects.geojson → carte_pastel_interactive.html
Script à lancer : web-maker.py et stats.py
```python3 web-maker.py
✅ Carte enregistrée dans 'carte_interactive.html'
```

