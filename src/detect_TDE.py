#!/usr/bin/env python3

import sys

from ovito.io import import_file
from ovito.modifiers import WignerSeitzAnalysisModifier



# ==========================================================
# ARGUMENT
# ==========================================================

if len(sys.argv) < 2: # On vérifie si on lance de la bonne façon le script


    print(
        "Usage : python3 detect_TDE.py trajectory.lammpstrj"
    )


    sys.exit(1)



trajectory = sys.argv[1]



# ==========================================================
# CHARGEMENT TRAJECTOIRE
# ==========================================================

pipeline = import_file(
    trajectory
) # On charge le fichier trajectory.lammpstrj et on le stock dans "pipeline" pour l'analyser



num_frames = pipeline.source.num_frames # On récupère le nombre de frame



print(
    f"Nombre de frames : {num_frames}"
)



# ==========================================================
# DERNIERE FRAME
# ==========================================================

last_frame = num_frames - 1



# ==========================================================
# ANALYSE WIGNER-SEITZ
# ==========================================================

modifier = WignerSeitzAnalysisModifier()  # Permet d'analyser les défauts


pipeline.modifiers.append(
    modifier
) # On ajoute le modifier au pipeline



data = pipeline.compute(
    last_frame
) # Stocke le résultat de l'analyse du modifier pour la dernière frame de pipeline



# ==========================================================
# RESULTATS
# ==========================================================

attributes = data.attributes # On filtre data pour ne garder que attributes à l'intérieur, les autres résultats ne nous intéressent pas 



vacancies = attributes.get(
    "WignerSeitz.vacancy_count",
    0
) # On récupère le nombre de lacunes



interstitials = attributes.get(
    "WignerSeitz.interstitial_count",
    0
) # On récupère le nombre d'intersticiels



print(
    "\nRésultat Wigner-Seitz :"
)


print(
    f"Vacances : {vacancies}"
)


print(
    f"Interstitials : {interstitials}"
)



# ==========================================================
# DECISION FRENKEL
# ==========================================================

if (

    vacancies >= 1

    and

    interstitials >= 1

):


    print(
        "YES"
    )


else:


    print(
        "NO"
    )
