import os
import time
from astropy.io import fits
import sirilpy as s


def process_images():
    # Capture du dossier de travail initial (ex: J:\260526_M40)
    dossier_parent = os.path.abspath(os.curdir)

    # Initialisation de l'interface native Siril
    siril = s.SirilInterface()

    try:
        siril.connect()
    except Exception as e:
        print(f"Erreur de connexion à Siril : {e}")
        return

    # requires 1.3.4

    # Convert Bias Frames to .fit files
    siril.cmd("cd", "biases")
    siril.cmd("convert", "bias", "-out=../process")
    siril.cmd("cd", "../process")

    # Stack Bias Frames to bias_stacked.fit
    siril.cmd("stack", "bias", "rej", "3", "3", "-nonorm", "-out=../masters/bias_stacked")
    siril.cmd("cd", "..")

    # Convert Flat Frames to .fit files
    siril.cmd("cd", "flats")
    siril.cmd("convert", "flat", "-out=../process")
    siril.cmd("cd", "../process")

    # Calibrate Flat Frames
    siril.cmd("calibrate", "flat", "-bias=../masters/bias_stacked")

    # Stack Flat Frames to pp_flat_stacked.fit
    siril.cmd("stack", "pp_flat", "rej", "3", "3", "-norm=mul", "-out=../masters/pp_flat_stacked")
    siril.cmd("cd", "..")

    # Convert Dark Frames to .fit files
    siril.cmd("cd", "darks")
    siril.cmd("convert", "dark", "-out=../process")
    siril.cmd("cd", "../process")

    # Stack Dark Frames to dark_stacked.fit
    siril.cmd("stack", "dark", "rej", "3", "3", "-nonorm", "-out=../masters/dark_stacked")
    siril.cmd("cd", "..")

    # Convert Light Frames to .fit files
    siril.cmd("cd", "lights")
    siril.cmd("convert", "light", "-out=../process")
    siril.cmd("cd", "../process")

    # Calibrate Light Frames
    siril.cmd(
        "calibrate",
        "light",
        "-dark=../masters/dark_stacked",
        "-flat=../masters/pp_flat_stacked",
        "-cc=dark",
        "-cfa",
        "-equalize_cfa",
        "-debayer",
    )

    # Align lights
    siril.cmd("register", "pp_light")

    # Stack calibrated lights to result.fit
    siril.cmd(
        "stack",
        "r_pp_light",
        "rej",
        "3",
        "3",
        "-norm=addscale",
        "-output_norm",
        "-rgb_equal",
        "-32b",
        "-out=result",
    )

    # flip if required
    siril.cmd("load", "result")
    siril.cmd("mirrorx", "-bottomup")

    # Sauvegarde sous un nom temporaire fixe dans le dossier parent
    siril.cmd("save", "../result_temp.fit")

    # On remonte dans le dossier parent dans Siril
    siril.cmd("cd", "..")

    # Construction du chemin du fichier temporaire basé sur le dossier d'origine
    fichier_temporaire = os.path.join(dossier_parent, "result_temp.fit")

    # Fermeture de la connexion à l'instance Siril
    siril.disconnect()

    # =====================================================================
    #  patch de l'entête FITS et renommage dynamique
    # =====================================================================

    # Temporisation : on attend que Siril lache le fichier temporaire
    time.sleep(2.0)

    # Configuration des parametres astro
    FOCALE = 1002.0
    PIXEL_SIZE = 3.72

    if os.path.exists(fichier_temporaire):
        try:
            # 1. Ouverture du fichier temporaire pour modification et lecture du LIVETIME
            with fits.open(fichier_temporaire, mode="update") as hdul:
                header = hdul[0].header

                # Récupération sécurisée du temps d'intégration réel
                livetime_sec = int(float(header.get("LIVETIME", 0)))

                # Injection des métadonnées forcées
                header["FOCALLEN"] = (FOCALE, "Focal length in mm (Forced)")
                header["XPIXSZ"] = (PIXEL_SIZE, "Pixel size X in um")
                header["YPIXSZ"] = (PIXEL_SIZE, "Pixel size Y in um")
                hdul.flush()

            # 2. Détermination du nom final basé sur le LIVETIME lu dans le FITS
            if livetime_sec > 0:
                nom_final = f"result_{livetime_sec}s.fit"
            else:
                nom_final = "result_final.fit"

            fichier_final = os.path.join(dossier_parent, nom_final)

            # 3. Renommage du fichier sur le disque
            if os.path.exists(fichier_final):
                os.remove(fichier_final)  # Évite les conflits si le fichier existe déjà
            os.rename(fichier_temporaire, fichier_final)

            print(
                f"Succes : Focale forcee a {FOCALE} mm. Fichier final genere : {fichier_final}"
            )

        except Exception as e:
            print(f"Erreur lors du traitement du fichier FITS : {e}")
    else:
        print(
            f"Erreur : Le fichier temporaire ({fichier_temporaire}) est introuvable."
        )


if __name__ == "__main__":
    process_images()