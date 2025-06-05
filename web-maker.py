import folium
import geopandas as gpd
import pandas as pd
import branca.colormap as cm
from folium.plugins import Fullscreen, MiniMap, MousePosition, MarkerCluster
from folium import Html

# === 1. Charger les trajets et reprojeter ===
gdf = gpd.read_file("data/trajects.geojson")
gdf = gdf.to_crs(epsg=3857)  # Pour calculer les longueurs en mètres
gdf["km"] = gdf.length / 1000  # Longueur en km

# === 2. Statistiques générales depuis un fichier texte ===
with open("output/statistiques.txt", "r", encoding="utf-8") as f:
    stats_content = f.read().replace("\n", "<br>")  # Pour affichage HTML

# === 3. Charger les stations Velib ===
df_stations = pd.read_csv("ressources/velib-emplacement-des-stations.csv", sep=";")
df_stations[['lat', 'lon']] = df_stations['Coordonnées géographiques'].str.split(',', expand=True).astype(float)

# === 4. Charger quartiers et reprojeter ===
quartiers = gpd.read_file("ressources/quartiers.geojson")
quartiers = quartiers.to_crs(epsg=3857)

joined = gpd.sjoin(quartiers, gdf, how="left", predicate="intersects")
trajets_par_quartier = joined.groupby(joined.index).agg({'count': 'sum'}).fillna(0)
quartiers['total_trajets'] = trajets_par_quartier['count']

# === 5. Palette de couleurs pour quartiers ===
vmin = quartiers['total_trajets'].min()
vmax = quartiers['total_trajets'].max()
palette = ['#f4cccc', '#f9cb9c', '#f6b26b', '#e06666', '#cc4125', '#6a0dad']
colormap_quartiers = cm.LinearColormap(colors=palette, vmin=vmin, vmax=vmax, caption='Trajets par quartier')

# === 6. Palette couleurs pour trajets ===
min_count = gdf["count"].min()
max_count = gdf["count"].max()
colors_trajets = ['#b19cd9', '#d8bfd8', '#f4cccc', '#f9cb9c', '#e06666']
colormap_trajets = cm.LinearColormap(colors=colors_trajets, vmin=min_count, vmax=max_count, caption='Nombre de trajets')
colormap_trajets.add_to = lambda m: m  # Hack pour compatibilité

# === 7. Créer la carte ===
center = [48.8566, 2.3522]  # Paris
m = folium.Map(location=center, zoom_start=13, tiles="CartoDB.Positron")

Fullscreen().add_to(m)
MiniMap(toggle_display=True, position="bottomleft").add_to(m)
MousePosition(
    position='bottomright',
    separator=' , ',
    prefix='Coordonnées:',
    lat_formatter="function(num) {return L.Util.formatNum(num, 5);}",
    lng_formatter="function(num) {return L.Util.formatNum(num, 5);}"
).add_to(m)

# === 8. Calque quartiers ===
def style_quartiers(feature):
    val = feature['properties']['total_trajets']
    if val is None:
        val = 0
    return {
        'fillColor': colormap_quartiers(val),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.4,
    }

quartiers_layer = folium.FeatureGroup(name="Quartiers par fréquentation", show=False)
folium.GeoJson(
    quartiers.to_crs(epsg=4326),
    style_function=style_quartiers,
    tooltip=folium.GeoJsonTooltip(fields=['l_qu', 'total_trajets'], aliases=['Quartier', 'Total trajets']),
).add_to(quartiers_layer)
quartiers_layer.add_to(m)
colormap_quartiers.add_to(m)

# === 9. Style trajets ===
def style_function(feature):
    count = feature['properties']['count']
    weight = 2 + (count / max_count * 6)
    return {
        'color': colormap_trajets(count),
        'weight': weight,
        'opacity': 0.85,
        'lineCap': 'round'
    }

colormap_trajets.add_to(m)

# === 10. Ajouter trajets ===
folium.GeoJson(
    data=gdf.to_crs(epsg=4326),
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=['count', 'km'],
        aliases=['Nombre de trajets', 'Longueur (km)'],
        sticky=True
    ),
    popup=folium.GeoJsonPopup(
        fields=['count', 'km'],
        aliases=['Nombre de trajets', 'Longueur (km)'],
        max_width=300
    ),
    name="Trajets Velib"
).add_to(m)

# === 11. Stations Velib avec cluster ===
stations_layer = folium.FeatureGroup(name="Stations Velib", show=True)
marker_cluster = MarkerCluster(name="Clusters stations").add_to(stations_layer)

for _, row in df_stations.iterrows():
    popup_html = f"""
    <b>{row['Nom de la station']}</b><br>
    Capacité : {row['Capacité de la station']} vélos<br>
    ID station : {row['Identifiant station']}
    """
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=4,
        color="#d36e70",
        fill=True,
        fill_color="#d36e70",
        fill_opacity=0.8,
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=row['Nom de la station'],
    ).add_to(marker_cluster)

stations_layer.add_to(m)

# === 12. Panneau statique avec le contenu brut du fichier ===
html_content = """
<div style='font-family: Arial; font-size: 14px; padding: 10px;'>
    <h4>📊 Statistiques</h4>
    <p>Trajet total, plus long trajet, stations les plus utilisées, etc.</p>
    <a href="stats.html" target="_blank" style='
        display: inline-block;
        padding: 10px 16px;
        background-color: #6a0dad;
        color: white;
        text-decoration: none;
        border-radius: 6px;
        font-weight: bold;
        transition: background-color 0.3s ease;
    ' onmouseover="this.style.backgroundColor='#8833cc'"
       onmouseout="this.style.backgroundColor='#6a0dad'">
        🔍 Voir les statistiques détaillées
    </a>
</div>
"""

html = folium.Html(html_content, script=True)
popup = folium.Popup(html, max_width=300)
marker = folium.Marker(location=[48.8566, 2.42], popup=popup, icon=folium.Icon(icon="info-sign"))
marker.add_to(m)

# === 13. Contrôle des calques ===
folium.LayerControl(position='topright').add_to(m)

# === 14. Export final ===
m.save("output/carte_interactive.html")
print("✅ Carte enregistrée dans 'carte_interactive.html'")
