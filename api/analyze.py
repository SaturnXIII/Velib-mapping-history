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
    On suppose que les objets JSON sont concaténés avec },{ sans tableau autour.
    Cette fonction isole chaque objet JSON.
    """
    pattern = re.compile(r'\{.*?\}(?=,?\{|\s*$)', re.DOTALL)
    return pattern.findall(text)

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

    # Extraction brute des objets JSON concaténés
    raw_objects = extract_json_objects(content)
    print(f"{len(raw_objects)} objets JSON extraits\n")

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

    for i, obj_str in enumerate(raw_objects, start=1):
        try:
            obj = json.loads(obj_str)
        except json.JSONDecodeError as e:
            print(f"[{i}] Erreur JSON: {e}")
            continue

        if 'parameter3' not in obj:
            continue
        p3 = obj['parameter3']

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

        out.write(f"Nombre total de vélos utilisés : {len(bike_counter)}\n")
        out.write(f"Vélos électriques (BIKEID < 50000) : {electric_count}\n")
        out.write(f"Vélos mécaniques (BIKEID >= 50000) : {mechanical_count}\n\n")

        out.write(f"Nombre de trajets électriques : {trajets_electric}\n")
        out.write(f"Nombre de trajets mécaniques : {trajets_mechanical}\n\n")

        out.write(f"Nombre de trajets boomerang (< 1 min) : {boomerang_count}\n")
        out.write(f"Nombre de trajets avec bonus > 0 : {trajets_with_bonus}\n")
        out.write(f"Minutes bonus gagnées au total : {total_bonus:.2f}\n")
        out.write(f"Distance totale parcourue : {total_distance:.1f} mètres\n")
        out.write(f"Distance moyenne par trajet : {avg_distance_km:.2f} km\n")
        out.write(f"Durée moyenne d'un trajet : {avg_duration_min:.2f} minutes\n")
        out.write(f"Vitesse moyenne globale : {avg_speed_global:.2f} km/h\n")
        out.write(f"Nombre total de trajets traités : {trajets_count}\n\n")

        out.write("Répartition des durées des trajets :\n")
        for label, count in duration_bins.items():
            percent = (count / trajets_count * 100) if trajets_count else 0
            out.write(f"{label} : {count} trajets ({percent:.1f}%)\n")
        out.write("\n")

        out.write("Trajets par heure (heure de départ) :\n")
        for hour in range(24):
            count = trajets_per_hour.get(hour, 0)
            out.write(f"{hour:02d}h : {count} trajets\n")
        out.write("\n")

        out.write("Trajets par jour (10 premiers jours) :\n")
        for day in sorted(trajets_per_day)[:10]:
            out.write(f"{day} : {trajets_per_day[day]} trajets\n")
        out.write("\n")

        out.write("🎉 Analyse terminée ! 🚴‍♂️ Merci pour les données ! 📊\n")

    print("✅ Statistiques écrites dans 'statistiques.txt'.")

if __name__ == "__main__":
    main()
