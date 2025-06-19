(async () => {
  try {
    // Envoi de la requête
    const response = await fetch('/api/private/getCourseList?limit=500000&offset=0', {
      method: 'GET',
      headers: {
        'Accept': 'application/json, text/plain, */*'
      },
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Erreur HTTP ${response.status}`);
    }

    // Récupération des données au format JSON
    const data = await response.json();

    // Convertir les données en chaîne de caractères (raw) pour un fichier texte
    const rawData = JSON.stringify(data, null, 2); // Formatée avec indentation pour meilleure lisibilité (tu peux enlever le "null, 2" si tu veux juste une version brute)

    // Créer un Blob pour convertir les données en fichier
    const blob = new Blob([rawData], { type: 'text/plain' });

    // Créer une URL pour le Blob
    const url = URL.createObjectURL(blob);

    // Créer un lien de téléchargement
    const a = document.createElement('a');
    a.href = url;
    a.download = 'data.txt'; // Nom du fichier
    a.textContent = 'Télécharger les données';

    // Ajouter ce lien à la page (optionnel, si tu veux cliquer pour télécharger)
    document.body.appendChild(a);
    a.click();

    // Libérer l'URL après téléchargement
    URL.revokeObjectURL(url);

    console.log('✅ Fichier téléchargé : data.txt');

  } catch (error) {
    console.error('❌ Erreur lors de la requête ou de l\'enregistrement du fichier :', error);
  }
})();
