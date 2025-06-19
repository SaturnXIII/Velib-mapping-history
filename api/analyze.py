import json
import os
import re
import subprocess
import requests
from collections import Counter, defaultdict
from datetime import datetime

def extract_json_objects(text):
    """
    Extrait des objets JSON contenus dans une chaîne texte.
    """
    try:
        # Essayer de charger tout le fichier JSON en une seule fois
        json_data = json.loads(text)
        # Si le JSON contient une clé 'walletOperations', on suppose qu'il y a plusieurs objets à traiter
        if 'walletOperations' in json_data:
            return json_data['walletOperations']
        else:
            print("Aucun objet trouvé dans 'walletOperations'.")
            return []
    except json.JSONDecodeError as e:
        print(f"Erreur JSON : {e}")
        return []

def parse_iso8601(date_str):
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")

def get_station_names():
    url = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_information.json"
    response = requests.get(url)
    info_data = response.json()

    station_dict = {}
    for station in info_data["data"]["stations"]:
        station_id = str(station["station_id"])
        station_name = station.get("name", f"Station {station_id}")
        station_dict[station_id] = station_name
    return station_dict

def main():
    if os.path.exists("../data/coordonnees.csv"):
        os.remove("../data/coordonnees.csv")
        print("Fichier 'coordonnees.csv' supprimé.\n")

    print("Chargement de data.txt...")
    with open('data.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    # Affiche les 500 premiers caractères du fichier pour vérifier son contenu
    print("Contenu de data.txt (500 premiers caractères) :")
    print(content[:500])  # Affiche les 500 premiers caractères du fichier

    # Extraction des objets JSON dans 'walletOperations'
    raw_objects = extract_json_objects(content)
    print(f"{len(raw_objects)} objets extraits\n")

    if len(raw_objects) == 0:
        print("Aucun objet JSON valide n'a été extrait.")
        return

    station_counter = Counter()
    trajet_durations = []
    trajet_speeds = []
    bike_counter = Counter()
    boomerang_count = 0
    total_bonus = 0.0
    total_distance = 0.0
    trajets_count = 0
    trajets_with_bonus = 0
    trajets_electric = 0
    trajets_mechanical = 0

    station_names = get_station_names()

    trajets_per_hour = defaultdict(int)
    trajets_per_day = defaultdict(int)

    for i, obj in enumerate(raw_objects, start=1):
        try:
            p3 = obj.get('parameter3', {})
            departure = p3.get('departureStationId')
            arrival = p3.get('arrivalStationId')
            bikeid = p3.get('BIKEID')
            bonus_earned = float(p3.get('BONUS_EARNED', 0))
            distance = float(p3.get('DISTANCE', 0))
            avg_speed = p3.get('AVERAGE_SPEED')
            avg_speed = float(avg_speed) if avg_speed is not None else None

            start = obj.get('startDate')
            end = obj.get('endDate')
            if start and end:
                try:
                    start_dt = parse_iso8601(start)
                    end_dt = parse_iso8601(end)
                except Exception as e:
                    print(f"[{i}] Erreur parsing dates : {e}")
                    continue

                duration_sec = (end_dt - start_dt).total_seconds()
                trajets_count += 1

                if departure:
                    station_counter[departure] += 1
                if arrival:
                    station_counter[arrival] += 1

                trajet_durations.append((duration_sec, departure, arrival))
                if avg_speed is not None:
                    trajet_speeds.append((avg_speed, departure, arrival))

                if bikeid:
                    bike_counter[bikeid] += 1
                    try:
                        if int(bikeid) < 50000:
                            trajets_electric += 1
                        else:
                            trajets_mechanical += 1
                    except ValueError:
                        pass

                if duration_sec < 60:
                    boomerang_count += 1

                total_bonus += bonus_earned
                if bonus_earned > 0:
                    trajets_with_bonus += 1

                total_distance += distance

                # Lancement de saver.py comme demandé
                cmd = ['python3', 'saver.py', str(departure), str(arrival)]
                print(f"[{i}] Lancement : {' '.join(cmd)}")
                subprocess.run(cmd)

                trajets_per_hour[start_dt.hour] += 1
                trajets_per_day[start_dt.date()] += 1

                if trajets_count % 10 == 0 or trajets_count == len(raw_objects):
                    percent = (trajets_count / len(raw_objects)) * 100
                    print(f"Trajets traités : {trajets_count}/{len(raw_objects)} ({percent:.1f}%)")

        except Exception as e:
            print(f"Erreur dans le traitement de l'objet #{i}: {e}")
            continue

    avg_duration_min = (sum(d for d, _, _ in trajet_durations) / len(trajet_durations) / 60) if trajet_durations else 0
    avg_speed_global = (sum(s for s, _, _ in trajet_speeds) / len(trajet_speeds)) if trajet_speeds else 0
    avg_distance_km = (total_distance / trajets_count / 1000) if trajets_count else 0

    duration_bins = {
        "<5 min": 0,
        "5-10 min": 0,
        "10-20 min": 0,
        "20-30 min": 0,
        ">30 min": 0
    }
    for duration_sec, _, _ in trajet_durations:
        minutes = duration_sec / 60
        if minutes < 5:
            duration_bins["<5 min"] += 1
        elif minutes < 10:
            duration_bins["5-10 min"] += 1
        elif minutes < 20:
            duration_bins["10-20 min"] += 1
        elif minutes < 30:
            duration_bins["20-30 min"] += 1
        else:
            duration_bins[">30 min"] += 1

    with open("../output/statistiques.txt", "w", encoding="utf-8") as out:
        out.write("--- Statistiques ---\n\n")

        out.write("Top 10 stations (départ + arrivée) :\n")
        for station, count in station_counter.most_common(10):
            name = station_names.get(str(station), f"Station {station}")
            out.write(f"{name} ({station}) : {count} passages\n")
        out.write("\n")

        out.write("Top 10 trajets les plus longs (en minutes) :\n")
        for duration, dep, arr in sorted(trajet_durations, reverse=True)[:10]:
            dep_name = station_names.get(str(dep), f"Station {dep}")
            arr_name = station_names.get(str(arr), f"Station {arr}")
            out.write(f"{dep_name} -> {arr_name} : {duration / 60:.2f} min\n")
        out.write("\n")

        out.write("Top 10 trajets les plus rapides (vitesse moyenne en km/h) :\n")
        for speed, dep, arr in sorted(trajet_speeds, reverse=True)[:10]:
            dep_name = station_names.get(str(dep), f"Station {dep}")
            arr_name = station_names.get(str(arr), f"Station {arr}")
            out.write(f"{dep_name} -> {arr_name} : {speed:.2f} km/h\n")
        out.write("\n")

        out.write("Top 10 vélos les plus utilisés :\n")
        for bikeid, count in bike_counter.most_common(10):
            out.write(f"Vélo {bikeid} : {count} trajets\n")
        out.write("\n")

        electric_count = sum(1 for bikeid in bike_counter if int(bikeid) < 50000)
        mechanical_count = len(bike_counter) - electric_count
        out.write(f"Nombre total de vélos électriques : {electric_count}\n")
        out.write(f"Nombre total de vélos mécaniques : {mechanical_count}\n")
        out.write("\n")

        out.write(f"Nombre de trajets avec bonus : {trajets_with_bonus} ({(trajets_with_bonus / trajets_count * 100) if trajets_count else 0:.2f}%)\n")
        out.write(f"Bonus total gagné : {total_bonus:.2f}\n")
        out.write(f"Distance parcourue au total (en km) : {total_distance / 1000:.2f}\n")
        out.write(f"Durée moyenne d'un trajet : {avg_duration_min:.2f} minutes\n")
        out.write(f"Vitesse moyenne globale : {avg_speed_global:.2f} km/h\n")
        out.write(f"Distance moyenne par trajet : {avg_distance_km:.2f} km\n")
        out.write("\n")

        out.write("Répartition des durées des trajets :\n")
        for bin_range, count in duration_bins.items():
            out.write(f"{bin_range} : {count}\n")
        out.write("\n")

        out.write("Répartition des trajets par heure :\n")
        for hour, count in sorted(trajets_per_hour.items()):
            out.write(f"{hour}:00 - {hour+1}:00 : {count}\n")
        out.write("\n")

        out.write("Répartition des trajets par jour :\n")
        for day, count in sorted(trajets_per_day.items()):
            out.write(f"{day} : {count}\n")
        out.write("\n")

    print("✅ Analyse terminée ! 🚴‍♂️ Merci pour les données ! 📊")

if __name__ == "__main__":
    main()
