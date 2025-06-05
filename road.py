import os
import osmnx as ox
import networkx as nx
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
from collections import defaultdict

# Configuration OSMNX
ox.settings.log_console = True
ox.settings.use_cache = True

# === Étape 1 : Charger les données de trajets ===
print("📥 Chargement des données de trajets...")
df = pd.read_csv("data/coordonnees.csv")  # Colonnes attendues : lat_start, lon_start, lat_end, lon_end
print(f"✅ {len(df)} trajets chargés.")

# === Étape 2 : Charger ou télécharger le graphe OSM ===
graph_filename = "ressources/paris_bike_10km.graphml"

if os.path.exists(graph_filename):
    print("📂 Chargement du graphe cyclable depuis le fichier local...")
    G = ox.load_graphml(graph_filename)
else:
    print("🌐 Téléchargement du graphe cyclable depuis OpenStreetMap...")
    city_center = (48.8566, 2.3522)  # Paris centre
    G = ox.graph_from_point(city_center, dist=10000, network_type='bike')
    ox.save_graphml(G, graph_filename)
    print(f"✅ Graphe sauvegardé sous {graph_filename}")

# Projeter le graphe pour des mesures précises
G_proj = ox.project_graph(G)

# === Étape 3 : Calcul des itinéraires ===
print("🚴 Calcul des itinéraires vélo...")
edge_usage = defaultdict(int)
total = len(df)

for idx, row in df.iterrows():
    try:
        # Nearest nodes doivent être appelés sur un graphe non projeté
        orig = ox.nearest_nodes(G, row['lon_start'], row['lat_start'])
        dest = ox.nearest_nodes(G, row['lon_end'], row['lat_end'])
        path = nx.shortest_path(G, orig, dest, weight='length')
        for u, v in zip(path[:-1], path[1:]):
            edge_usage[(u, v)] += 1
    except Exception as e:
        print(f"❌ Trajet {idx+1}/{total} ignoré (erreur : {e})")

print(f"✅ {len(edge_usage)} segments utilisés au total.")

# === Étape 4 : Construction des géométries GeoJSON ===
print("🧱 Création des géométries pour GeoJSON...")
features = []

for (u, v), count in edge_usage.items():
    try:
        data = G_proj.get_edge_data(u, v)[0]
        geom = data['geometry'] if 'geometry' in data else LineString([
            (G_proj.nodes[u]['x'], G_proj.nodes[u]['y']),
            (G_proj.nodes[v]['x'], G_proj.nodes[v]['y'])
        ])
        features.append({'geometry': geom, 'count': count})
    except Exception as e:
        print(f"⚠️ Erreur sur le segment ({u}, {v}): {e}")

# Création du GeoDataFrame avec géométrie
gdf = gpd.GeoDataFrame(features, geometry="geometry")
gdf.set_crs(G_proj.graph['crs'], inplace=True)

# === Étape 5 : Export GeoJSON ===
output_file = "data/trajects.geojson"
print(f"💾 Sauvegarde dans '{output_file}'...")
gdf.to_file(output_file, driver="GeoJSON")
print(f"✅ Fichier GeoJSON généré avec {len(gdf)} lignes.")
