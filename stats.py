import re
import json

def parse_stats_file(file_path):
    """Parse le fichier de statistiques et extrait toutes les données"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    stats = {}
    
    # Extraire les statistiques générales
    stats['total_trips'] = int(re.search(r'Nombre total de trajets traités : (\d+)', content).group(1))
    stats['total_bikes'] = int(re.search(r'Nombre total de vélos utilisés : (\d+)', content).group(1))
    stats['electric_bikes'] = int(re.search(r'Vélos électriques.*: (\d+)', content).group(1))
    stats['mechanical_bikes'] = int(re.search(r'Vélos mécaniques.*: (\d+)', content).group(1))
    stats['electric_trips'] = int(re.search(r'Nombre de trajets électriques : (\d+)', content).group(1))
    stats['mechanical_trips'] = int(re.search(r'Nombre de trajets mécaniques : (\d+)', content).group(1))
    stats['boomerang_trips'] = int(re.search(r'Nombre de trajets boomerang.*: (\d+)', content).group(1))
    stats['bonus_trips'] = int(re.search(r'Nombre de trajets avec bonus > 0 : (\d+)', content).group(1))
    stats['bonus_minutes'] = float(re.search(r'Minutes bonus gagnées au total : ([\d.]+)', content).group(1))
    
    # Distance et vitesse
    distance_m = float(re.search(r'Distance totale parcourue : ([\d.]+)', content).group(1))
    stats['total_distance_km'] = round(distance_m / 1000, 0)
    stats['avg_distance_km'] = float(re.search(r'Distance moyenne par trajet : ([\d.]+)', content).group(1))
    stats['avg_duration_min'] = float(re.search(r'Durée moyenne d\'un trajet : ([\d.]+)', content).group(1))
    stats['avg_speed_kmh'] = float(re.search(r'Vitesse moyenne globale : ([\d.]+)', content).group(1))
    
    # Top 10 stations
    stations_section = re.search(r'Top 10 stations.*?:(.*?)(?=Top 10|$)', content, re.DOTALL).group(1)
    stats['top_stations'] = []
    for line in stations_section.strip().split('\n'):
        if line.strip():
            match = re.search(r'(.*?) \((\d+)\) : (\d+) passages', line)
            if match:
                stats['top_stations'].append({
                    'name': match.group(1).strip(),
                    'id': match.group(2),
                    'count': int(match.group(3))
                })
    
    # Top 10 trajets rapides
    fast_section = re.search(r'Top 10 trajets les plus rapides.*?:(.*?)(?=Top 10|Nombre total)', content, re.DOTALL).group(1)
    stats['fast_trips'] = []
    for line in fast_section.strip().split('\n'):
        if line.strip() and ' -> ' in line:
            match = re.search(r'(.*?) -> (.*?) : ([\d.]+) km/h', line)
            if match:
                stats['fast_trips'].append({
                    'from': match.group(1).strip(),
                    'to': match.group(2).strip(),
                    'speed': float(match.group(3))
                })
    
    # Répartition des durées
    duration_section = re.search(r'Répartition des durées.*?:(.*?)(?=Trajets par heure)', content, re.DOTALL).group(1)
    stats['duration_distribution'] = {}
    for line in duration_section.strip().split('\n'):
        if line.strip():
            if '<5 min' in line:
                match = re.search(r'<5 min : \d+ trajets \(([\d.]+)%\)', line)
                stats['duration_distribution']['<5min'] = float(match.group(1))
            elif '5-10 min' in line:
                match = re.search(r'5-10 min : \d+ trajets \(([\d.]+)%\)', line)
                stats['duration_distribution']['5-10min'] = float(match.group(1))
            elif '10-20 min' in line:
                match = re.search(r'10-20 min : \d+ trajets \(([\d.]+)%\)', line)
                stats['duration_distribution']['10-20min'] = float(match.group(1))
            elif '20-30 min' in line:
                match = re.search(r'20-30 min : \d+ trajets \(([\d.]+)%\)', line)
                stats['duration_distribution']['20-30min'] = float(match.group(1))
            elif '>30 min' in line:
                match = re.search(r'>30 min : \d+ trajets \(([\d.]+)%\)', line)
                stats['duration_distribution']['>30min'] = float(match.group(1))
    
    # Trajets par heure
    hourly_section = re.search(r'Trajets par heure.*?:(.*?)(?=Trajets par jour|$)', content, re.DOTALL).group(1)
    stats['hourly_trips'] = []
    for line in hourly_section.strip().split('\n'):
        if line.strip() and 'h : ' in line:
            match = re.search(r'(\d+)h : (\d+) trajets', line)
            if match:
                hour = int(match.group(1))
                trips = int(match.group(2))
                stats['hourly_trips'].append({'hour': f'{hour:02d}h', 'trips': trips})
    
    return stats

def generate_html(stats, output_path):
    """Génère le fichier HTML avec les statistiques"""
    
    # Générer les top stations HTML
    top_stations_html = ""
    for i, station in enumerate(stats['top_stations'][:10], 1):
        colors = ['#ff9ff3', '#7c3aed', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b']
        color = colors[min(i-1, len(colors)-1)]
        
        top_stations_html += f'''
            <div class="list-item">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div class="rank">{i}</div>
                    <div>
                        <strong>{station['name']}</strong><br>
                        <small style="color: #718096;">ID: {station['id']}</small>
                    </div>
                </div>
                <div style="font-weight: 700; color: {color};">{station['count']} passages</div>
            </div>'''
    
    # Générer les trajets rapides HTML
    fast_trips_html = ""
    for i, trip in enumerate(stats['fast_trips'][:10], 1):
        colors = ['#ff9ff3', '#7c3aed', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b']
        color = colors[min(i-1, len(colors)-1)]
        
        fast_trips_html += f'''
            <div class="list-item">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div class="rank">{i}</div>
                    <div><strong>{trip['from']} → {trip['to']}</strong></div>
                </div>
                <div style="font-weight: 700; color: {color};">{trip['speed']} km/h</div>
            </div>'''
    
    # Données JavaScript pour les graphiques
    hourly_data_js = json.dumps(stats['hourly_trips'])
    
    html_content = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Statistiques Vélib 🚴‍♂️</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #ffeef8 0%, #f0f8ff 50%, #f5fff5 100%);
            min-height: 100vh;
            color: #4a5568;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .header {{
            text-align: center;
            padding: 3rem 0;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 30px;
            margin-bottom: 3rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);
        }}

        .header h1 {{
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #ff9ff3, #7c3aed, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }}

        .header p {{
            font-size: 1.2rem;
            color: #64748b;
            opacity: 0.8;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }}

        .stat-card {{
            background: rgba(255, 255, 255, 0.8);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #ffc0cb, #e6e6fa, #b0e0e6, #f0fff0);
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        }}

        .stat-card h3 {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .stat-value {{
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }}

        .stat-label {{
            font-size: 0.9rem;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .top-list {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08);
        }}

        .top-list h2 {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }}

        .list-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            margin-bottom: 0.8rem;
            background: linear-gradient(90deg, rgba(255, 192, 203, 0.1), rgba(230, 230, 250, 0.1));
            border-radius: 12px;
            border-left: 4px solid;
            transition: all 0.3s ease;
        }}

        .list-item:nth-child(odd) {{
            border-left-color: #ffc0cb;
        }}

        .list-item:nth-child(even) {{
            border-left-color: #e6e6fa;
        }}

        .list-item:hover {{
            transform: translateX(5px);
            background: linear-gradient(90deg, rgba(255, 192, 203, 0.2), rgba(230, 230, 250, 0.2));
        }}

        .rank {{
            background: linear-gradient(135deg, #ff9ff3, #7c3aed);
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.9rem;
        }}

        .chart-container {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08);
        }}

        .chart-bar {{
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            gap: 1rem;
        }}

        .chart-label {{
            min-width: 60px;
            font-weight: 600;
            color: #4a5568;
        }}

        .bar {{
            flex: 1;
            height: 30px;
            border-radius: 15px;
            position: relative;
            overflow: hidden;
            background: rgba(200, 200, 200, 0.2);
        }}

        .bar-fill {{
            height: 100%;
            border-radius: 15px;
            transition: width 1s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-weight: 600;
            font-size: 0.8rem;
        }}

        .hour-0 {{ background: linear-gradient(90deg, #ff9ff3, #ffc0cb); }}
        .hour-6 {{ background: linear-gradient(90deg, #7c3aed, #a78bfa); }}
        .hour-12 {{ background: linear-gradient(90deg, #06b6d4, #67e8f9); }}
        .hour-18 {{ background: linear-gradient(90deg, #10b981, #6ee7b7); }}

        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}

        .summary-card {{
            background: rgba(255, 255, 255, 0.8);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
            transition: transform 0.3s ease;
        }}

        .summary-card:hover {{
            transform: translateY(-3px);
        }}

        .duration-distribution {{
            display: flex;
            gap: 0.5rem;
            margin: 1rem 0;
            height: 40px;
        }}

        .duration-bar {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            font-size: 0.8rem;
            transition: all 0.3s ease;
        }}

        .duration-bar:hover {{
            transform: scale(1.05);
        }}

        .d1 {{ background: linear-gradient(135deg, #ff9ff3, #ffc0cb); }}
        .d2 {{ background: linear-gradient(135deg, #7c3aed, #a78bfa); }}
        .d3 {{ background: linear-gradient(135deg, #06b6d4, #67e8f9); }}
        .d4 {{ background: linear-gradient(135deg, #10b981, #6ee7b7); }}
        .d5 {{ background: linear-gradient(135deg, #f59e0b, #fbbf24); }}

        .footer {{
            text-align: center;
            padding: 2rem;
            color: #718096;
            font-size: 1.1rem;
        }}

        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .stat-card, .top-list, .chart-container {{
            animation: slideIn 0.6s ease forwards;
        }}

        .emoji {{
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚴‍♂️ Dashboard Vélib Statistiques</h1>
            <p>Analyse complète de vos trajets cyclistes parisiens</p>
        </div>

        <div class="summary-cards">
            <div class="summary-card">
                <div class="stat-value" style="color: #ff9ff3;">{stats['total_trips']:,}</div>
                <div class="stat-label">Trajets totaux</div>
            </div>
            <div class="summary-card">
                <div class="stat-value" style="color: #7c3aed;">{stats['total_bikes']:,}</div>
                <div class="stat-label">Vélos utilisés</div>
            </div>
            <div class="summary-card">
                <div class="stat-value" style="color: #06b6d4;">{int(stats['total_distance_km']):,} km</div>
                <div class="stat-label">Distance totale</div>
            </div>
            <div class="summary-card">
                <div class="stat-value" style="color: #10b981;">{stats['avg_distance_km']:.1f} km</div>
                <div class="stat-label">Distance moyenne</div>
            </div>
            <div class="summary-card">
                <div class="stat-value" style="color: #f59e0b;">{int(stats['avg_duration_min'])} min</div>
                <div class="stat-label">Durée moyenne</div>
            </div>
            <div class="summary-card">
                <div class="stat-value" style="color: #ef4444;">{stats['avg_speed_kmh']:.1f} km/h</div>
                <div class="stat-label">Vitesse moyenne</div>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3><span class="emoji">⚡</span> Vélos Électriques</h3>
                <div class="stat-value" style="color: #06b6d4;">{stats['electric_bikes']}</div>
                <div class="stat-label">vélos ({stats['electric_trips']} trajets)</div>
            </div>
            <div class="stat-card">
                <h3><span class="emoji">🔧</span> Vélos Mécaniques</h3>
                <div class="stat-value" style="color: #10b981;">{stats['mechanical_bikes']}</div>
                <div class="stat-label">vélos ({stats['mechanical_trips']} trajets)</div>
            </div>
            <div class="stat-card">
                <h3><span class="emoji">🎯</span> Trajets Boomerang</h3>
                <div class="stat-value" style="color: #f59e0b;">{stats['boomerang_trips']}</div>
                <div class="stat-label">trajets < 1 minute</div>
            </div>
            <div class="stat-card">
                <h3><span class="emoji">🎁</span> Bonus Gagnés</h3>
                <div class="stat-value" style="color: #ef4444;">{int(stats['bonus_minutes'])}</div>
                <div class="stat-label">minutes ({stats['bonus_trips']} trajets)</div>
            </div>
        </div>

        <div class="top-list">
            <h2><span class="emoji">🏆</span> Top 10 Stations les Plus Fréquentées</h2>
            {top_stations_html}
        </div>

        <div class="top-list">
            <h2><span class="emoji">🚀</span> Top 10 Trajets les Plus Rapides</h2>
            {fast_trips_html}
        </div>

        <div class="chart-container">
            <h2><span class="emoji">⏰</span> Répartition des Trajets par Heure</h2>
            <div id="hourlyChart"></div>
        </div>

        <div class="chart-container">
            <h2><span class="emoji">⏱️</span> Répartition des Durées</h2>
            <div class="duration-distribution">
                <div class="duration-bar d1">
                    &lt;5min<br>{stats['duration_distribution']['<5min']:.1f}%
                </div>
                <div class="duration-bar d2">
                    5-10min<br>{stats['duration_distribution']['5-10min']:.1f}%
                </div>
                <div class="duration-bar d3">
                    10-20min<br>{stats['duration_distribution']['10-20min']:.1f}%
                </div>
                <div class="duration-bar d4">
                    20-30min<br>{stats['duration_distribution']['20-30min']:.1f}%
                </div>
                <div class="duration-bar d5">
                    &gt;30min<br>{stats['duration_distribution']['>30min']:.1f}%
                </div>
            </div>
        </div>

        <div class="footer">
            <p>🎉 Analyse terminée ! 🚴‍♂️ Merci pour les données ! 📊</p>
        </div>
    </div>

    <script>
        // Données des trajets par heure
        const hourlyData = {hourly_data_js};

        // Générer le graphique par heure
        const maxTrips = Math.max(...hourlyData.map(d => d.trips));
        const hourlyChart = document.getElementById('hourlyChart');

        hourlyData.forEach(data => {{
            const chartBar = document.createElement('div');
            chartBar.className = 'chart-bar';
            
            const percentage = (data.trips / maxTrips) * 100;
            let colorClass = 'hour-0';
            const hour = parseInt(data.hour);
            
            if (hour >= 6 && hour < 12) colorClass = 'hour-6';
            else if (hour >= 12 && hour < 18) colorClass = 'hour-12';
            else if (hour >= 18 && hour < 24) colorClass = 'hour-18';
            
            chartBar.innerHTML = `
                <div class="chart-label">${{data.hour}}</div>
                <div class="bar">
                    <div class="bar-fill ${{colorClass}}" style="width: ${{percentage}}%">
                        ${{data.trips}}
                    </div>
                </div>
            `;
            
            hourlyChart.appendChild(chartBar);
        }});

        // Animation d'entrée pour les barres
        setTimeout(() => {{
            document.querySelectorAll('.bar-fill').forEach((bar, index) => {{
                setTimeout(() => {{
                    bar.style.width = bar.style.width;
                }}, index * 50);
            }});
        }}, 500);
    </script>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    """Fonction principale"""
    stats_file = "output/statistiques.txt"  # Chemin vers votre fichier de stats
    output_file = "output/dashboard_stats.html"  # Fichier HTML de sortie
    
    try:
        # Parser les statistiques
        print("📊 Parsing des statistiques...")
        stats = parse_stats_file(stats_file)
        
        # Générer le HTML
        print("🚀 Génération du dashboard HTML...")
        generate_html(stats, output_file)
        
        print(f"✅ Dashboard généré avec succès : {output_file}")
        
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {stats_file} n'existe pas.")
    except Exception as e:
        print(f"❌ Erreur lors de la génération : {e}")

if __name__ == "__main__":
    main()
