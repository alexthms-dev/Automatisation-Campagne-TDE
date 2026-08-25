#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys



# ==========================================================
# PARAMETRES
# ==========================================================
# Chemins

HOME = Path.home()


SIMU_DIR = (
    HOME /
    "simu_campagne_test_Ge"
)



RELAX_SUB = (
    SIMU_DIR /
    "sub_relaxation.sh"
)


RESTART_FILE = (
    SIMU_DIR /
    "relaxed_Ge.restart"
)



# ==========================================================
# ARGUMENTS
# ==========================================================

if len(sys.argv) < 3:

    print(
        "Usage : python3 launch_TDE.py energie directions_actives.txt" # Vérifie si on le lance correctement
    )

    sys.exit(1)


ENERGY = float(sys.argv[1])


DIRECTIONS_FILE = Path(sys.argv[2])



# ==========================================================
# LECTURE DIRECTIONS ACTIVES
# ==========================================================
# Lit le fichier directions_actives.txt

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


            directions.append(line) # ajoute les directions dans la liste


    return directions



# ==========================================================
# NOM DOSSIER DIRECTION
# ==========================================================

def direction_to_name(
        direction):


    vx, vy, vz = map(
        float,
        direction.split()
    )


    return (

        f"dir_{vx:.6f}_"
        f"{vy:.6f}_"
        f"{vz:.6f}"

    )



# ==========================================================
# LANCEMENT RELAXATION
# ==========================================================
# Lancement du SUB de la relaxation

def launch_relaxation():


    print(
        "\nSoumission de la relaxation...\n"
    )


    if not RELAX_SUB.exists():

        print(
            "Erreur : sub_relaxation.sh absent."
        )

        sys.exit(1)



    result = subprocess.run(   # permet de lancer une commande comme si elle était écrite dans le terminal

        [

            "sbatch",

            RELAX_SUB.name

        ],

        cwd=SIMU_DIR,  # Current Working Directory (le dossier depuis lequel la commande va être exécutée)

        capture_output=True,  # récupére ce que la commande écrit dans le terminal (returncode, stdout ou stderr ; ex : Submitted batch job 123456)

        text=True # le récupère sous forme de chaînes de caractères

    )



    if result.returncode != 0:


        print(
            "Erreur pendant la soumission de la relaxation."
        )


        print(
            result.stderr
        )


        sys.exit(1)



    output = result.stdout.strip() # enlève les espaces et retour à la ligne en trop


    print(
        f"{output}"
    )



    # Exemple :
    # Submitted batch job 123456

    job_id = output.split()[-1] # extrait l'id du job


    return job_id
    
# ==========================================================
# LANCEMENT JOBS TDE AVEC DEPENDANCE
# ==========================================================
# Lancement des SUB des énergies des directions, en prenant en compte le fait que la relaxation soit faite ou non

def launch_jobs(
        directions,
        relax_job_id=None):


    print(
        f"\nSoumission des TDE {ENERGY} eV...\n"
    )


    launched = 0



    for direction in directions:


        dirname = direction_to_name(
            direction
        )


        energy_dir = (

            SIMU_DIR
            /
            dirname
            /
            f"{ENERGY}eV"

        )



        script = (

            energy_dir
            /
            "sub"

        )



        if not script.exists():


            print(
                f"⚠ Script absent : {script}"
            )

            continue



        # Si une relaxation vient d'être soumise, on attend sa fin avec une dépendance Slurm, sinon on lance directement les TDE.

        if relax_job_id is not None:


            command = [

                "sbatch",

                f"--dependency=afterok:{relax_job_id}", # donne la condition d'attendre que la relaxation se termine avant de lancer le calcul

                script.name

            ]


        else:


            command = [

                "sbatch",

                script.name

            ]



        result = subprocess.run(

            command,

            cwd=energy_dir,

            capture_output=True,

            text=True

        )

    # Même chose pour pour la relaxation :

        if result.returncode == 0:


            print(

                f"{dirname} {ENERGY} eV : "
                f"{result.stdout.strip()}"

            )


            launched += 1



        else:


            print(
                f"Erreur pour {dirname}"
            )


            print(
                result.stderr
            )



    print(
        f"\n{launched} jobs TDE soumis."
    )



# ==========================================================
# PROGRAMME PRINCIPAL
# ==========================================================

if __name__ == "__main__":


    print(
        "\n================================="
    )

    print(
        f"LANCEMENT TDE : {ENERGY} eV"
    )

    print(
        "=================================\n"
    )



    directions = load_directions()



    print(
        f"{len(directions)} directions actives trouvées.\n"
    )



    if len(directions) == 0:


        print(
            "Aucune direction active."
        )

        sys.exit(0)



    # Vérification dossier principal

    if not SIMU_DIR.exists():

        print(
            "Erreur : dossier de campagne absent."
        )

        print(
            SIMU_DIR
        )

        sys.exit(1)
        
    # ======================================================
    # VERIFICATION RELAXATION
    # ======================================================

    if RESTART_FILE.exists():


        print(
            "Structure relaxée déjà présente."
        )


        print(
            "  Relaxation ignorée."
        )


        relax_job_id = None



    else:


        relax_job_id = launch_relaxation()


        print(
            f"\nRelaxation soumise avec le job ID : {relax_job_id}"
        )



    # ======================================================
    # SOUMISSION DES JOBS TDE
    # ======================================================

    launch_jobs(

        directions,

        relax_job_id

    )



    print(
        "\n================================="
    )

    print(
        "Fin des soumissions."
    )

    print(
        "================================="
    )
