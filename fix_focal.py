# =====================================================================
#     recherche d'un fichier results_xxxxs.fit
#     verification coherence (le fichier doit etre 'récent'
#     patch de la focal length 'FOCALLEN' dans l'entête FITS
# =====================================================================

import os
import glob
import time
from astropy.io import fits

# 1. Temporisation : on attend que Siril lache completement le fichier
time.sleep(2.0)
SEUIL_SECONDES = 120

# 2. Configuration des parametres astro
FOCALE = 1002.0
PIXEL_SIZE = 3.72


# 3. Recherche des fichiers sans le '../' car le dossier courant est J:\260526_M40
liste_fichiers = glob.glob("result_*s.fit")

if not liste_fichiers:
    print("Erreur : Aucun fichier correspondant a 'result_*s.fit' n'a ete trouve.")
else:
    fichier_trouve = None
    temps_actuel = time.time()
    
    # 4. Parcours des fichiers pour trouver le plus recent
    for f in liste_fichiers:
        temps_modification = os.path.getmtime(f)
        ecart = abs(temps_actuel - temps_modification)
        
        if ecart <= SEUIL_SECONDES:
            fichier_trouve = f
            print(f"Fichier valide detecte (Ecart: {ecart:.1f} s) : {f}")
            break

    # 5. Modification des metadonnees du fichier valide
    if fichier_trouve:
        try:
            with fits.open(fichier_trouve, mode='update') as hdul:
                header = hdul[0].header
                header['FOCALLEN'] = (FOCALE, 'Focal length in mm (Forced)')
                header['XPIXSZ'] = (PIXEL_SIZE, 'Pixel size X in um')
                header['YPIXSZ'] = (PIXEL_SIZE, 'Pixel size Y in um')
                hdul.flush()
            print(f"Succes : Focale forcee a {FOCALE} mm pour {fichier_trouve}.")
        except Exception as e:
            print(f"Erreur lors de l'ecriture du fichier FITS : {e}")
    else:
        print("Securite : Aucun fichier modifie recemment n'a ete valide.")