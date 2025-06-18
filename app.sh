#!/bin/sh
echo "Installation des dépendances..." | lolcat
pip install -r requirements.txt
echo "Lancement de api/analyze.py..." | lolcat
cd api
python3 analyze.py
echo "✅ Fin d'exécution de api/analyze.py" | lolcat

cd ..
echo "Lancement de road.py..." | lolcat
python3 road.py
echo "🚦 Fin d'exécution de road.py" | lolcat

echo "Lancement de web-maker.py..."
python3 web-maker.py
echo "🌐 Fin d'exécution de web-maker.py" | lolcat

echo "Lancement de stats.py..."
python3 stats.py
echo "Fin d'exécution de stats.py" | lolcat


# Afficher "Velib'" en ASCII art avec figlet
if command -v figlet >/dev/null 2>&1; then
    figlet "Velib'" | lolcat
else
    echo "figlet n'est pas installé." | lolcat
fi
echo "Votre carte velib' est disponible dans le dossier output ✨" | lolcat
