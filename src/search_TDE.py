#!/usr/bin/env python3

from pathlib import Path
import subprocess
import time



# ==========================================================
# PARAMETRES
# ==========================================================

START_ENERGY = 6.0

MAX_ENERGY = 60.0

ENERGY_STEP = 0.5

WAIT_TIME = 150   # temps que l'on attend avant de vérifier si tout les calculs sont finis (en secondes) 

HOME = Path.home()

SIMU_DIR = HOME / "simu_campagne_test_Ge"

DIRECTIONS_FILE = Path(
    "directions_actives.txt"
)

RESULT_FILE = Path(
    "TDE_results.txt"
)

# ==========================================================
# STOCKAGE RESULTATS
# ==========================================================

TDE_RESULTS = {}



# ==========================================================
# LECTURE DIRECTIONS
# ==========================================================

def load_directions():


    directions = []


    with open(
        DIRECTIONS_FILE,
        "r"
    ) as f:


        for line in f:


            line = line.strip()


            if not line or line.startswith("#"):

                continue


            directions.append(line)


    return directions



# ==========================================================
# ECRITURE DIRECTIONS RESTANTES
# ==========================================================

def write_directions(
        directions):


    with open(      # On ouvre le fichier en "w" donc on efface tout son contenu puis on réécrit les directions restantes
        DIRECTIONS_FILE,
        "w"
    ) as f:


        for direction in directions:


            f.write(
                direction + "\n"
            )



# ==========================================================
# ECRITURE RESULTATS TDE
# ==========================================================

# ici même chose, on l'ouvre en "w" donc ça efface tout et on réécrit tout, on a le dictionnaire TDE_RESULTS qui est déjà associé ou pas encore à une énergie

def write_results():


    with open(
        RESULT_FILE,
        "w"
    ) as f:


        f.write(
            "=================================\n"
        )


        f.write(
            "Résultats TDE Ge\n"
        )


        f.write(
            "=================================\n\n"
        )



        for direction, energy in sorted( #ici le sorted tri les direction et non leur valeur en énergie, ce n'est pas nécessaire mais ça peut aider pour retrouver plus facilement des directions
            TDE_RESULTS.items()
        ):


            f.write(

                f"{direction:<45} {energy} eV\n"  # écrit les directions associée ou non à l'énergie

            )



        f.write(
            "\n=================================\n"
        )


        f.write(

            f"Nombre de directions trouvees : "
            f"{len(TDE_RESULTS)}\n"

        )



# ==========================================================
# GENERATION + LANCEMENT CALCUL
# ==========================================================

# Prépare les dossiers et fichiers de l'énergie en question pour les directions restantes

def launch_energy(
        energy):


    print(
        f"\n===== {energy} eV =====\n"
    )


    subprocess.run(

        [

            "python3",

            "generate_TDE.py",

            str(energy),

            str(DIRECTIONS_FILE)

        ]

    )


# Lance les calculs

    subprocess.run(

        [

            "python3",

            "launch_TDE.py",

            str(energy),

            str(DIRECTIONS_FILE)

        ]

    )


# ==========================================================
# ATTENTE FIN CALCULS
# ==========================================================

# Attend que les calculs soient tous terminé pour passer à l'énergie suivante

def wait_results(
        energy,
        directions):


    print(
        "\nAttente des calculs..."
    )



    while True:


        finished = 0



        for direction in directions:

# map() : applique la fonction à tout les éléments (ici applique float
# direction.split() : sépare les 3 composantes de direction
            vx, vy, vz = map(
                float,
                direction.split()
            )


            dirname = (

                f"dir_{vx:.6f}_"
                f"{vy:.6f}_"
                f"{vz:.6f}"

            )

# On créé le chemin pour le fichier "DONE" qui dira si le calcul est fini, ce fichier est créé dans le input.lammps, à la fin du calcul

            done = (

                SIMU_DIR

                /

                dirname

                /

                f"{energy}eV"

                /

                "DONE"

            )



            if done.exists():

                finished += 1



        print(

            f"{finished}/{len(directions)} "
            "calculs termines"

        )



        if finished == len(directions): # si tous les calculs ont créé "DONE", on sort de la boucle

            break



        time.sleep(
            WAIT_TIME
        )



# ==========================================================
# ANALYSE OVITO
# ==========================================================

def analyse_results(
        energy,
        directions):


    remaining = []


    print(
        "\nAnalyse Wigner-Seitz..."
    )



    for direction in directions:


        vx, vy, vz = map(
            float,
            direction.split()
        )


        dirname = (

            f"dir_{vx:.6f}_"
            f"{vy:.6f}_"
            f"{vz:.6f}"

        )



        trajectory = (

            SIMU_DIR

            /

            dirname

            /

            f"{energy}eV"

            /

            "trajectory.lammpstrj"

        )


# On lance l'analyse

        result = subprocess.run(

            [

                "python3",

                "detect_TDE.py",

                str(trajectory)

            ],

            capture_output=True, # On récupère la réponse de detect_TDE.py

            text=True

        )



        answer = result.stdout.strip()  # On stocke la réponse dans "answer"



        if "YES" in answer:


            print(

                f"{dirname} : TDE = {energy} eV"

            )


            TDE_RESULTS[dirname] = energy  # On ajoute la valeur de l'énergie à la direction associée dans le dictionnaire 


            write_results()  # On réécrit par dessus le fichier résultats



        else:


            print(

                f"{dirname} : pas de Frenkel"

            )


            remaining.append(
                direction
            ) # On ajoute la direction actuelle dans remaining car l'énergie n'est pas suffisante



    return remaining



# ==========================================================
# PROGRAMME PRINCIPAL
# ==========================================================

if __name__ == "__main__":


    directions = load_directions()



    print(

        f"{len(directions)} directions initiales"

    )



    energy = START_ENERGY



    while (

        directions

        and

        energy <= MAX_ENERGY

    ):



        print(
            "\n---------------------------------"
        )


        print(
            f"ENERGIE : {energy} eV"
        )


        print(
            "---------------------------------\n"
        )



        write_directions(
            directions
        )



        launch_energy(
            energy
        )



        wait_results(

            energy,

            directions

        )



        directions = analyse_results(

            energy,

            directions

        ) #la nouvelle valeur de direction est "remaining"



        print(

            f"\nDirections restantes : "
            f"{len(directions)}"

        )



        energy += ENERGY_STEP



    write_results()



    print(
        "\n================================="
    )


    print(
        "Recherche TDE terminee."
    )


    print(
        "Resultats dans TDE_results.txt"
    )


    print(
        "================================="
    )
