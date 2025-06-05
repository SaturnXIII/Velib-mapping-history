import requests
import sys
import csv
import os

# Vérifie les arguments
if len(sys.argv) != 3:
    print("❌ Utilisation : python3 save.py <start_station_id> <end_station_id>")
    sys.exit(1)

start_id = sys.argv[1]
end_id = sys.argv[2]

# URL de l'API
info_url = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_information.json"
info_data = requests.get(info_url).json()

# Fonction pour extraire les coordonnées et le nom d'une station
def get_station_info(station_id):
    station = next((s for s in info_data["data"]["stations"] if str(s["station_id"]) == station_id), None)
    if station:
        return station.get("name"), station.get("lat"), station.get("lon")
    else:
        print(f"❌ Station avec ID {station_id} non trouvée.")
        sys.exit(1)

# Récupère infos de chaque station
name_start, lat_start, lon_start = get_station_info(start_id)
name_end, lat_end, lon_end = get_station_info(end_id)

# 🖨️ Affiche les noms des stations
print(f"🚲 Station de départ : {name_start}")
print(f"🏁 Station d'arrivée : {name_end}")

# 📄 Écriture dans le fichier CSV (mode ajout)
file_path = "../data/coordonnees.csv"
file_exists = os.path.isfile(file_path)

with open(file_path, mode="a", newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    if not file_exists or os.stat(file_path).st_size == 0:
        writer.writerow(["lat_start", "lon_start", "lat_end", "lon_end"])
    writer.writerow([lat_start, lon_start, lat_end, lon_end])

print("✅ Coordonnées ajoutées à coordonnees.csv")
