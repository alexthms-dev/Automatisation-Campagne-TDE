#!/usr/bin/env python3

from pathlib import Path
import shutil
import math
import sys


# ==========================================================
# PARAMETRES UTILISATEUR
# ==========================================================

if len(sys.argv) < 3: # oblige à avoir les arguments directions et energies

    print(
        "Usage : python3 generate_TDE.py energie directions_actives.txt"
    )

    sys.exit(1)


ENERGY = float(sys.argv[1])

DIRECTIONS_FILE = Path(sys.argv[2])

NPROC = 8  # Nombre de coeurs pour le calcul


ACCOUNT = "team_m3"

PARTITION = "m3"



# ==========================================================
# CHEMINS
# ==========================================================

HOME = Path.home()


SIMU_DIR = (
    HOME /
    "simu_campagne_test_Ge"
)


SCRATCH_DIR = (
    HOME /
    "scratch"
)


IMAGE = (
    HOME /
    "image" /
    "lammps-milady.sif"
)


INPUT_TEMPLATE = (
    SCRATCH_DIR /
    "input.lammps"
)


RELAX_INPUT = (
    SCRATCH_DIR /
    "input_relaxation.lammps"
)


REFERENCE_FILE = (
    SCRATCH_DIR /
    "reference.lmp"
)


POTENTIAL_FILE = (
    SCRATCH_DIR /
    "lammps_bso4_qnml1_params.pot"
)



# ==========================================================
# CONSTANTES PHYSIQUES
# ==========================================================

MASS = 72.64


EV_TO_J = 1.602176634e-19

AVOGADRO = 6.02214076e23

# Conversion pour les unités de l'input
CONVERSION = (

    0.01
    *
    math.sqrt(
        2
        *
        EV_TO_J
        *
        AVOGADRO
        /
        1e-3
    )

)

# ==========================================================
# LECTURE DES DIRECTIONS
# ==========================================================
# Lit les directions du fichier directions_actives.txt

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


            directions.append(line) # récupère la direction sur la ligne et la place dans directions


    return directions


# ==========================================================
# NOM DOSSIER DIRECTION
# ==========================================================

def direction_to_name(
        direction):

# map() : applique la fonction à tout les éléments (ici applique float
# direction.split() : sépare les 3 composantes de direction
    vx, vy, vz = map(  
        float,
        direction.split() 
    )


    return (

        f"dir_{vx:.6f}_"
        f"{vy:.6f}_"
        f"{vz:.6f}"

    ) # arrondie à 6 chiffres après la virgule



# ==========================================================
# CALCUL VITESSE PKA
# ==========================================================
# Permet de convertir l'énergie et la direction en entrée en vitesse suivant x y et z pour les inputs de LAMMPS 

def compute_velocity(
        direction,
        energy):

# map() : applique la fonction à tout les éléments (ici applique float
# direction.split() : sépare les 3 composantes de direction

    vx_dir, vy_dir, vz_dir = map(
        float,
        direction.split()
    )

    print(f"direction = {direction}")

    print(f"vx_dir = {vx_dir}")
    print(f"vy_dir = {vy_dir}")
    print(f"vz_dir = {vz_dir}")
    
    dir_norm = math.sqrt(vx_dir**2 + vy_dir**2 + vz_dir**2) # normalisation
    
    print(f"dir_norm = {dir_norm}")

    speed = (

        CONVERSION
        *
        math.sqrt(
            energy / MASS
        )

    )
    
    print(f"vitesse = {speed}")

    vx = (speed * vx_dir) / dir_norm

    vy = (speed * vy_dir) / dir_norm

    vz = (speed * vz_dir) / dir_norm

    print(f"vx = {vx}")
    print(f"vy = {vy}")
    print(f"vz = {vz}")

    return vx, vy, vz



# ==========================================================
# NETTOYAGE RESULTATS PRECEDENTS
# ==========================================================
# Au cas ou je relance par dessus, pour ne pas avoir de problème

def clean_previous_results(
        energy_dir):


    files = [

        "trajectory.lammpstrj",

        "fin.lammpstrj",

        "finalrelax.lammpstrj",

        "log.lammps",

        "slurm.out",

        "slurm.err",

        "DONE"

    ]


    for filename in files:


        file = energy_dir / filename


        if file.exists():

            file.unlink()



# ==========================================================
# PREPARATION DOSSIER PRINCIPAL
# ==========================================================
# Transfert les fichiers nécéssaires dans le fichier principal

def prepare_main_directory():


    print(
        "Préparation du dossier principal..."
    )


    SIMU_DIR.mkdir(
        parents=True, # permet de ne pas créer d'erreur si les dossiers parents n'existent pas
        exist_ok=True # permet de ne pas créer d'erreur si le dossier existe déjà
    )


    files = [

        INPUT_TEMPLATE,

        RELAX_INPUT,

        REFERENCE_FILE,

        POTENTIAL_FILE

    ]


    for file in files:


        shutil.copy2(

            file,

            SIMU_DIR / file.name # ici le / est pour le chemin, ce n'est pas une division

        ) # Copie les fichiers "files" vers le nouvel emplacement (ici le dossier principal)


        print(
            f" {file.name} créé"
        )


    print()
    
# ==========================================================
# GENERATION SUB RELAXATION
# ==========================================================
#Créé le fichier Sub de la relaxation pour ne pas avoir à le recalculer plusieurs fois

def generate_relaxation_sub():


    print(
        "Création du sub de relaxation..."
    )


    sub_file = (
        SIMU_DIR /
        "sub_relaxation.sh"
    )


    with open(
        sub_file,
        "w"
    ) as f:


        f.write(
            "#!/bin/sh\n\n"
        )


        f.write(
            "#SBATCH --job-name=relax_Ge\n"
        )


        f.write(
            "#SBATCH --output=slurm_relax.out\n"
        )


        f.write(
            "#SBATCH --error=slurm_relax.err\n\n"
        )


        f.write(
            f"#SBATCH --account={ACCOUNT}\n"
        )


        f.write(
            f"#SBATCH --partition={PARTITION}\n"
        )


        f.write(
            f"#SBATCH --ntasks={NPROC}\n"
        )


        f.write(
            "#SBATCH --cpus-per-task=1\n\n"
        )
        

        f.write(
            "#SBATCH --mem=2G\n\n"
        )


        f.write(
            f"cd {SIMU_DIR}\n\n"
        )


        f.write(

            f"apptainer exec {IMAGE} "
            f"mpirun -np {NPROC} lmp "
            "-in input_relaxation.lammps\n"

        )


    print(
        f" {sub_file} créé"
    )


    print()



# ==========================================================
# CREATION ARBORESCENCE
# ==========================================================
# Créer les dossiers directions et énergies pour avoir une arborescence propre

def create_directories(
        directions):


    print(
        "Création des dossiers TDE..."
    )


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


        energy_dir.mkdir(
            parents=True,  # permet de ne pas créer d'erreur si les dossiers parents n'existent pas
            exist_ok=True  # permet de ne pas créer d'erreur si le dossier existe déjà
        )


        clean_previous_results(
            energy_dir
        )


        print(
            f" {energy_dir} créé"
        )


    print()
    
# ==========================================================
# GENERATION INPUTS TDE
# ==========================================================
# Récupère le fichier input de base et modifie les vitesses vx vy et vz pour les bonnes énergies et directions données 

def generate_inputs(directions):

    for direction in directions:

        dirname = direction_to_name(direction)

        energy_dir = (
            SIMU_DIR /
            dirname /
            f"{ENERGY}eV"
        )

        print(f"ENERGY = {ENERGY}eV")

        input_file = energy_dir / "input.lammps" # C'est juste le chemin, actuellement le fichier d'input n'est pas dans le dossier 


        shutil.copy2(
            INPUT_TEMPLATE,
            input_file
        ) # C'est ici qu'on copie l'input dans le dossier


        vx, vy, vz = compute_velocity(
            direction,
            ENERGY
        )


        velocity_command = (
            f"velocity PKA set "
            f"{vx:.6f} "
            f"{vy:.6f} "
            f"{vz:.6f} "
            f"units box"
        ) # Permettra d'écrire la bonne ligne dans l'input


        with open(input_file,"r") as f:
            lines = f.readlines() # Copie toute les lignes du fichier et les met dans "lines"


        with open(input_file,"w") as f:   # ouvrir avec "w" efface son contenue donc on réécrit le fichier entièrement grâce à "lines" et on remplace la ligne concernant l'énergie du PKA grâce à velocity_command

            for line in lines:

                if line.strip().startswith(
                    "velocity PKA set"
                ):

                    f.write(
                        velocity_command+"\n"
                    )

                else:

                    f.write(line)

# ==========================================================
# GENERATION SUB TDE
# ==========================================================
#Créé les SUB des énergies et direction donnée

def generate_sub_scripts(
        directions):


    print(
        "Création des scripts SLURM..."
    )


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


        sub_file = (
            energy_dir /
            "sub"
        )


        with open(
            sub_file,
            "w"
        ) as f:


            f.write(
                "#!/bin/sh\n\n"
            )


            f.write(

                f"#SBATCH --job-name=TDE_{dirname}_{ENERGY}eV\n"

            )


            f.write(

                f"#SBATCH --output={energy_dir}/slurm.out\n"

            )


            f.write(

                f"#SBATCH --error={energy_dir}/slurm.err\n\n"

            )


            f.write(

                f"#SBATCH --account={ACCOUNT}\n"

            )


            f.write(

                f"#SBATCH --partition={PARTITION}\n"

            )


            f.write(

                f"#SBATCH --ntasks={NPROC}\n"

            )


            f.write(

                "#SBATCH --cpus-per-task=1\n"

            )

            
            f.write(
                "#SBATCH --mem=2G\n\n"

            )


            f.write(

                f"cd {energy_dir}\n\n"

            )


            f.write(

                f"apptainer exec {IMAGE} "
                f"mpirun -np {NPROC} lmp "
                "-in input.lammps\n"

            )


        print(
            f" {sub_file} créé"
        )


    print()
    
    
# ==========================================================
# PROGRAMME PRINCIPAL
# ==========================================================

if __name__ == "__main__":


    print(
        "\n================================="
    )

    print(
        f"GENERATION TDE : {ENERGY} eV"
    )

    print(
        "=================================\n"
    )



    directions = load_directions()



    print(
        f"{len(directions)} directions chargées\n"
    )



    if len(directions) == 0:


        print(
            "Aucune direction active."
        )

        sys.exit(0)



    # Préparation du dossier principal
    prepare_main_directory()



    # Création du script de relaxation  (voir pour une amélioration : ne le faire qu'une seule fois car je crois que ça le refait à chaque fois (ça ne change pas grand chose mais ça peut optimiser le travail et rendre plus propre))
    
    generate_relaxation_sub() 



    # Création des dossiers dir/energie
    create_directories(
        directions
    )



    # Génération des inputs TDE
    generate_inputs(
        directions
    )



    # Génération des scripts SLURM
    generate_sub_scripts(
        directions
    )



    print(
        "================================="
    )

    print(
        "Generation terminee."
    )

    print(
        "================================="
    )
