"""
Configuration des secteurs d'activité selon la table de référence
"""

# Table des secteurs d'activité
SECTEURS = {
    "01": "SIEGE SCENIQUE",
    "02": "SIEGE BUREAU & MOBILIER ACCUEIL",
    "03": "AMEUBLEMENT",
    "04": "MEDICAL",
    "05": "FERROVIAIRE",
    "06": "EMBALLAGE",
    "07": "CARAVANING",
    "08": "BATIMENT",
    "09": "PARTICULIERS",
    "10": "NAUTISME",
    "11": "DIVERS",
    "12": "BAGAGERIE",
    "13": "ARMEMENT"
}

# Mots-clés associés à chaque secteur pour la classification automatique
SECTEUR_KEYWORDS = {
    "01": ["scène", "scénique", "théâtre", "opéra", "spectacle", "concert"],
    "02": ["bureau", "accueil", "chaise", "fauteuil", "siège", "mobilier de bureau"],
    "03": ["ameublement", "meuble", "mobilier", "décoration", "intérieur"],
    "04": ["médical", "santé", "hôpital", "clinique", "médecine"],
    "05": ["ferroviaire", "train", "rail", "sncf", "wagon", "locomotive"],
    "06": ["emballage", "packaging", "conditionnement", "carton"],
    "07": ["caravaning", "camping-car", "caravane", "mobile-home"],
    "08": ["bâtiment", "construction", "chantier", "btp", "immobilier"],
    "09": ["particulier", "privé", "personnel", "individuel"],
    "10": ["nautisme", "bateau", "voilier", "yacht", "naval", "maritime"],
    "11": ["divers"],
    "12": ["bagagerie", "valise", "sac", "bagage"],
    "13": ["armement", "défense", "militaire", "arme"]
}

# Correspondance clients connus - secteur
CLIENT_SECTORS = {
    "sokoa": "02",
    "quinette": "01", 
    "eurosit": "02",
    "kleslo": "01",
    "oxeti": "02",
    "diva salon": "03",
    "roset": "03",
    "compin": "05",
    "airbus": "13",
    "dassault": "13",
    "safran": "13",
    "thales": "13",
    "promotal": "04"
}
