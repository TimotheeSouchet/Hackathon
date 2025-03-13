import librosa  # Librairie spécialisée dans le traitement du son
import matplotlib.pyplot as plt  # Librairie pour l'affichage des graphiques
import numpy as np  # Librairie pour les calculs mathématiques et la manipulation des tableaux
from math import sqrt  # Importation de la fonction racine carrée
import os  # Module permettant la gestion des fichiers et dossiers
from duree import *  # Importation de toutes les fonctions du module 'duree' (utilisé pour format_duree)

# Demande à l'utilisateur d'entrer le chemin du dossier contenant les fichiers audio à analyser
dossier = input("Veuillez entrer le chemin complet vers votre répertoire de retour des capteurs journaliers : ")

# Vérification si le dossier existe avant de continuer
if not os.path.isdir(dossier):
    print("Le dossier spécifié n'existe pas. Veuillez vérifier le chemin.")
    exit()  # Arrête le programme si le dossier est introuvable

# Définition de la fonction permettant de traiter un fichier audio
def TraitementAudio(fichier):
    """
    Analyse un fichier audio pour détecter le passage d'un rat à partir des valeurs RMS (Root Mean Square).
    Retourne une probabilité (0 : aucune, 1 : faible, 2 : moyenne, 3 : forte).
    """
    try:
        # Chargement du fichier audio avec sa fréquence d'échantillonnage
        y, sr = librosa.load(fichier, sr=None)

        # Définition de la durée de chaque segment analysé (en secondes)
        dureesegment = 3  
        fenetreTaille = int(sr * dureesegment)  # Calcul de la taille de la fenêtre en échantillons

        # Liste pour stocker les valeurs RMS des segments analysés
        rmc_values = []

        # Découpe du signal en segments de 3 secondes et calcul du RMS
        for i in range(0, len(y), fenetreTaille):
            segment = y[i:i + fenetreTaille]  # Extraction du segment
            rmc = sqrt(np.sum(segment**2) / len(segment))  # Calcul de la valeur RMS
            rmc_values.append(rmc)

        # Initialisation de la probabilité de passage du rat et du temps correspondant
        proba = 0  
        temps = 0  

        # Analyse des valeurs RMS pour estimer la probabilité
        for i in range(len(rmc_values)):
            if rmc_values[i] > 0.4:  # Seuil élevé : Forte probabilité
                temps = i * 3  # Calcul du temps estimé du passage
                proba = max(proba, 3)
            elif rmc_values[i] > 0.25:  # Seuil moyen : Probabilité moyenne
                temps = i * 3
                proba = max(proba, 2)
            elif rmc_values[i] > 0.1:  # Seuil bas : Faible probabilité
                temps = i * 3
                proba = max(proba, 1)

        # Affichage du résultat basé sur la probabilité détectée
        if proba == 1:
            print(f"Faible probabilité de passage d'un rat dans {fichier} à {format_duree(temps)} sec.")
            return 1
        elif proba == 2:
            print(f"Moyenne probabilité de passage d'un rat dans {fichier} à {format_duree(temps)} sec.")
            return 2
        elif proba == 3:
            print(f"Forte probabilité de passage d'un rat dans {fichier} à {format_duree(temps)} sec.")
            return 3
        else:
            print(f"Aucun passage détecté dans {fichier}.")
            return 0

    except Exception as e:
        print(f"Erreur lors du traitement du fichier {fichier}: {e}")
        return -1  # Code d'erreur en cas de problème

# Définition de la fonction permettant d'afficher la forme d'onde du fichier audio
def AffichagePlot(fichier):
    """
    Affiche la forme d'onde d'un fichier audio.
    """
    try:
        # Chargement du fichier audio
        y, sr = librosa.load(fichier, sr=None)

        # Création de la figure pour l'affichage de la forme d'onde
        plt.figure(figsize=(14, 5))
        librosa.display.waveshow(y, sr=sr)  # Affichage du signal sous forme de graphe
        plt.title('Forme d\'onde')
        plt.xlabel("Temps (s)")
        plt.ylabel('Amplitude')
        plt.show()

    except Exception as e:
        print(f"Erreur lors de l'affichage du fichier {fichier}: {e}")

# Parcours du dossier et traitement des fichiers audio (.wav)
for fichier in os.listdir(dossier):
    if fichier.endswith(".wav"):  # Vérifie si le fichier est un fichier audio au format WAV
        cheminComplet = os.path.join(dossier, fichier)  # Construction du chemin complet du fichier
        TraitementAudio(cheminComplet)  # Analyse du fichier audio
        AffichagePlot(cheminComplet)  # Affichage de la forme d'onde du fichier audio
