import numpy as np
import pyvista as pv
import re
from scipy.spatial import Delaunay


# ============================================================
# LECTURE DES RESULTATS TDE
# ============================================================

def lire_resultats(fichier):

    directions = []
    energies = []

    pattern = re.compile(  # sert à créer un motif de recherche qui pourra ensuite être utiliser pour chercher des lignes correspondant à ce format. Ici les group se trouveront avec les parenthèse.
        r"dir_"
        r"([-+]?\d*\.?\d+)_" # group 1
        r"([-+]?\d*\.?\d+)_" # group 2
        r"([-+]?\d*\.?\d+)" # group 3
        r"\s+"
        r"([-+]?\d*\.?\d+)" # group 4
        r"\s*eV"
    )

    with open(fichier, "r", encoding="utf-8") as f:  # "utf-8" : indique à Python comment interpréter les caractères du fichier

        for ligne in f:

            match = pattern.search(ligne)  # Demande grâce au pattern si la ligne correspond au format que l'on cherche

            if match:

                x = float(match.group(1))
                y = float(match.group(2))
                z = float(match.group(3))

                energie = float(match.group(4))

                directions.append([x, y, z])  # On ajoute dans la liste
                energies.append(energie)  # On ajoute dans la liste

    directions = np.array(  # On les transforme en tableau (car plus pratique pour les calculs)
        directions,
        dtype=float
    )

    energies = np.array(  # On les transforme en tableau (car plus pratique pour les calculs)
        energies,
        dtype=float
    )

    if len(directions) == 0:  # au cas ce n'est pas le bon fichier (ou si il est vide)
        raise ValueError(
            f"Aucune direction trouvée dans {fichier}"
        )

    return directions, energies


# ============================================================
# CREATION DES POINTS SUR LA SPHERE
# ============================================================

def creer_points_sphere(   # multiplie juste les directions avec le rayon de la sphère
    directions,
    rayon=1.0
):

    directions = np.asarray(  # np.asarray même chose que np.array, c'est juste que si directions est déjà un tableau, ça ne fera pas une copie pour rien, ça va juste le laisser pareil
        directions,
        dtype=float
    )

    return directions * rayon


# ============================================================
# CREATION DE LA SURFACE TDE
# ============================================================

def creer_surface_tde(
    directions,
    energies,
    rayon=1.0
):
    """
    Crée la surface triangulée correspondant au domaine
    couvert par les directions calculées.

    L'énergie est uniquement utilisée comme couleur.
    """

    points = creer_points_sphere(  # On créé les points de la sphère (qui correspondent aux mesures)
        directions,
        rayon
    )

    # Projection XY pour la triangulation
    xy = directions[:, :2]  # xy devient un tableau avec seulement les x et les y de directions

    triangulation = Delaunay(xy)  # ici on à un problème de surface donc 2D c'est pourquoi on ne prend que x et y, si on prenait z en plus, ça ferait des tetraèdres à l'intérieur de la sphère. C'est seulement pour créer les triangles pour l'interpolation

    faces = []

    for triangle in triangulation.simplices:  # triangulation.simplices : contient les indices des points qui constituent chaque triangle.

        i, j, k = triangle  # chaque lettre est un sommet du triangle

        faces.append([
            3,  # juste pour dire que le polygone possède 3 sommets
            i,
            j,
            k
        ])

    faces = np.array(  # On transforme en tableau 
        faces,
        dtype=np.int64
    ).flatten()  # On aplatit le tableau (c'est le format attendu ici par PyVista)

    mesh = pv.PolyData(  # Ici on créer le maillage des triangles c'est à dire qu'on "nomme" les points des triangles : points = coordonnées des sommets et faces = quels sommets doivent être reliés
        points,
        faces
    )

    mesh["TDE"] = energies  # On ajoute au points du maillage un donnée appelée "TDE" qui correspond à l'énergie

    return mesh


# ============================================================
# AJOUT DE LA SPHERE COMPLETE
# ============================================================

def ajouter_sphere_complete(
    plotter,  # l'objet PyVista dans lequel on ajoute la sphère.
    rayon=1.0,  # le rayon de la sphère
    opacite=0.2,  # sa transparence
    couleur="lightgray"  # sa couleur
):
    """
    Ajoute une sphère complète servant de repère visuel, indépendante de la surface TDE.

    """

    sphere = pv.Sphere(  # Création de la sphère
        radius=rayon,
        center=(0.0, 0.0, 0.0),
        theta_resolution=80,  # résolution de la sphère (car ce n'est pas un rond parfait, c'est plein de petits polygones
        phi_resolution=80  # même chose
    )

    plotter.add_mesh(  # On ajoute la sphère dans plotter pour l'afficher de la bonne façon
        sphere,
        color=couleur,
        opacity=opacite,
        smooth_shading=False,  # éclairage de la sphère
        show_edges=False   # les arretes des polygones de la sphère
    )


# ============================================================
# AJOUT DE LA SURFACE TDE
# ============================================================

def ajouter_surface_tde(
    plotter,
    mesh,  # Le maillage des triangles Delaunay
    energies,
    opacite=0.7,  #  opacite :  0.0 -> transparente / 1.0 -> opaque
    cmap="turbo" # palette de couleurs utilisée pour les différentes valeur de TDE
):
    """
    Ajoute la surface TDE. C'est ici qu'on détermine les couleurs.
    Les sommets sont associé à une couleur et l'interpolation se fait automatiquement
    (grâce aux triangles et leurs sommets).

    """

    plotter.add_mesh(  # On ajoute le maillage à la scène "plotter"
        mesh,
        scalars="TDE", # Utilise les valeurs contenues dans "TDE" pour déterminer la couleur
        cmap=cmap, # On associe la palette de couleurs
        clim=[
            energies.min(), # debut de la palette
            energies.max() # fin de la palette
        ],
        opacity=opacite,
        show_edges=False,
        smooth_shading=True,
        scalar_bar_args={  # Configuration de la barre de la palette de couleurs affichée à coté de la sphère
            "title": "TDE (eV)",
            "vertical": True,
        },
    )


# ============================================================
# AJOUT DES POINTS DE CALCUL
# ============================================================

def ajouter_points_calcules(
    plotter,
    directions,
    rayon=1.0,
    couleur="black",
    taille=12
):
    """
    Affiche les positions exactes des directions calculées.
    """

    points = creer_points_sphere(  # On donne la position aux points sur la sphère
        directions,
        rayon
    )

    nuage = pv.PolyData(points) # On transforme ces points en objet PolyData

    plotter.add_mesh( # On ajoute les points à la scène
        nuage, 
        color=couleur,
        point_size=taille, # Taille d'affichage, le rayon ne sera pas constant par rapport à la sphère totale
        render_points_as_spheres=True,  # On rend les points comme étant de petites sphères
    )


# ============================================================
# CREATION DES POSITIONS ATOMIQUES
# ============================================================

def creer_positions_atomiques(
    ux,
    uy,
    uz,
    distances
):
    """
    Permet d'afficher les atomes à l'intérieur de la sphère afin de visualiser la structure atomique
    On n'affiche pas le PKA ici, il est géré par une autre fonction

    Retourne :
        positions : tableau (N, 3) avec N : nombre d'atome
    """
    
    # On les transforme en tableaux

    ux = np.asarray(
        ux,
        dtype=float
    )

    uy = np.asarray(
        uy,
        dtype=float
    )

    uz = np.asarray(
        uz,
        dtype=float
    )

    distances = np.asarray(
        distances,
        dtype=float
    )

    if not (  # On verifie si les tableaux sont bien de la même taille
        len(ux)
        == len(uy)
        == len(uz)
        == len(distances)
    ):
        raise ValueError(
            "ux, uy, uz et distances doivent "
            "avoir le même nombre d'éléments."
        )

    # On calcule la norme des vecteurs pour ensuite les normaliser
    normes = np.sqrt(
        ux**2 +
        uy**2 +
        uz**2
    )

    # Normalisation
    uxN = ux / normes
    uyN = uy / normes
    uzN = uz / normes

    # Coordonnées cartésiennes
    x = distances * uxN
    y = distances * uyN
    z = distances * uzN

    positions = np.column_stack( # On met tout ça dans un tableau
        (x, y, z)
    )

    return positions


# ============================================================
# AJOUT DES ATOMES
# ============================================================

def ajouter_atomes(
    plotter,
    positions,
    rayon=0.08,
    couleur="gray"
):
    """
    Ajoute les atomes sous forme de sphères.
    """

    positions = np.asarray(
        positions,
        dtype=float
    )

    for position in positions:

        sphere = pv.Sphere( # On créé tout les atomes en tant qu'objet
            radius=rayon,
            center=position,
            theta_resolution=20,
            phi_resolution=20
        )

        plotter.add_mesh( # On ajoute les atomes à la scène
            sphere,
            color=couleur,
            smooth_shading=True
        )


# ============================================================
# AJOUT DU PKA
# ============================================================

def ajouter_pka(
    plotter,
    position=(0.0, 0.0, 0.0),
    rayon=0.08,
    couleur="red"
):
    """
    Ajoute le PKA au centre de la structure.
    """

    sphere = pv.Sphere(
        radius=rayon,
        center=position,
        theta_resolution=20,
        phi_resolution=20
    )

    plotter.add_mesh(
        sphere,
        color=couleur,
        smooth_shading=True
    )


# ============================================================
# AJOUT DES AXES
# ============================================================

def ajouter_axes(plotter):
    """
    Ajoute la triade XYZ.
    """

    plotter.add_axes(
        interactive=False, # On ne peux pas cliquer dessus
        line_width=3, # On définit l'épaisseur des lignes des axes
        labels_off=False  # On désactive le fait de ne pas afficher les XYZ (donc on les affiche)
    )


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():

    # ========================================================
    # PARAMETRES
    # ========================================================

    fichier = "TDE_results.txt"

    # --------------------------------------------------------
    # Rayon de la sphère TDE
    # --------------------------------------------------------
    #

    rayon_sphere = 1.0

    # --------------------------------------------------------
    # Opacité du domaine TDE
    # --------------------------------------------------------

    opacite = 0.7

    # --------------------------------------------------------
    # Opacité de la sphère complète
    # --------------------------------------------------------
    #
    # Très faible pour que les atomes restent visibles.

    opacite_sphere = 0.2

    # --------------------------------------------------------
    # Rayon des atomes
    # --------------------------------------------------------

    rayon_atome = 0.08

    # --------------------------------------------------------
    # Constante de maille
    # --------------------------------------------------------
    #
    # Ici on met 1 pour que ça colle bien à la sphère mais on pourrait mettre la vraie valeur (5.67 pour le Ge) et dans ce cas mettre le même paramètre pour le rayon des sphères

    a_maille = 1


    # ========================================================
    # DIRECTIONS DES ATOMES
    # ========================================================
    
    # C'est ici qu'on donne l'emplacement des atomes

    ux = np.array([
        1, -1, -1, 1,
        1, -1, 1, -1,
        1, -1, 1, -1,
        0, 0, 0, 0,
        3, 3, 1, 1, 1, 1,
        -1, -1, -1, -1,
        -3, -3,
        1, 0, 0, -1, 0, 0
    ])


    uy = np.array([
        1, -1, 1, -1,
        1, 1, -1, -1,
        0, 0, 0, 0,
        1, -1, 1, -1,
        1, -1,
        3, 1, -1, -3,
        3, 1, -1, -3,
        1, -1,
        0, 1, 0, 0, -1, 0
    ])


    uz = np.array([
        1, 1, -1, -1,
        0, 0, 0, 0,
        1, 1, -1, -1,
        1, 1, -1, -1,
        -1, 1,
        -1, -3, 3, 1,
        1, 3, -3, -1,
        1, -1,
        0, 0, 1, 0, 0, -1
    ])


    # ========================================================
    # DISTANCES DES ATOMES AU CENTRE
    # ========================================================

    S = a_maille * np.array([

        np.sqrt(3) / 4,
        np.sqrt(3) / 4,
        np.sqrt(3) / 4,
        np.sqrt(3) / 4,

        1 / np.sqrt(2),
        1 / np.sqrt(2),
        1 / np.sqrt(2),
        1 / np.sqrt(2),
        1 / np.sqrt(2),
        1 / np.sqrt(2),
        1 / np.sqrt(2),
        1 / np.sqrt(2),
        1 / np.sqrt(2),
        1 / np.sqrt(2),
        1 / np.sqrt(2),
        1 / np.sqrt(2),

        np.sqrt(11) / 4,
        np.sqrt(11) / 4,
        np.sqrt(11) / 4,
        np.sqrt(11) / 4,
        np.sqrt(11) / 4,
        np.sqrt(11) / 4,
        np.sqrt(11) / 4,
        np.sqrt(11) / 4,
        np.sqrt(11) / 4,
        np.sqrt(11) / 4,
        np.sqrt(11) / 4,
        np.sqrt(11) / 4,

        1,
        1,
        1,
        1,
        1,
        1

    ], dtype=float)


    # ========================================================
    # CREATION DES POSITIONS ATOMIQUES
    # ========================================================

    positions_atomiques = creer_positions_atomiques(
        ux,
        uy,
        uz,
        S
    )


    # ========================================================
    # LECTURE DES RESULTATS TDE
    # ========================================================

    directions, energies = lire_resultats(
        fichier
    )


    # ========================================================
    # INFORMATIONS
    # ========================================================

    print()
    print("=================================")
    print("Résultats TDE Ge")
    print("=================================")

    print(
        f"Nombre de directions : "
        f"{len(directions)}"
    )

    print(
        f"TDE minimale : "
        f"{energies.min():.2f} eV"
    )

    print(
        f"TDE maximale : "
        f"{energies.max():.2f} eV"
    )

    print(
        f"Nombre d'atomes voisins : "
        f"{len(positions_atomiques)}"
    )

    print(
        "PKA : position (0, 0, 0)"
    )

    print("=================================")
    print()


    # ========================================================
    # CREATION DE LA SURFACE TDE
    # ========================================================

    surface = creer_surface_tde(
        directions,
        energies,
        rayon=rayon_sphere
    )


    # ========================================================
    # CREATION DU PLOTTER
    # ========================================================

    plotter = pv.Plotter()  # On créé le plotter

    plotter.set_background(  # On défini la couleur de fond de scène
        "white"
    )


    # ========================================================
    # SPHERE COMPLETE
    # ========================================================
    #
    # Elle est légèrement plus petite que la surface TDE
    # pour éviter les problèmes de superposition.

    ajouter_sphere_complete(
        plotter,
        rayon=rayon_sphere * 0.995,
        opacite=opacite_sphere,
        couleur="lightgray"
    )


    # ========================================================
    # SURFACE TDE
    # ========================================================

    ajouter_surface_tde(
        plotter,
        surface,
        energies,
        opacite=opacite
    )


    # ========================================================
    # POINTS DE CALCUL
    # ========================================================

    ajouter_points_calcules(
        plotter,
        directions,
        rayon=rayon_sphere,
        couleur="black",
        taille=12
    )


    # ========================================================
    # ATOMES
    # ========================================================

    ajouter_atomes(
        plotter,
        positions_atomiques,
        rayon=rayon_atome,
        couleur="gray"
    )


    # ========================================================
    # PKA
    # ========================================================

    ajouter_pka(
        plotter,
        position=(0.0, 0.0, 0.0),
        rayon=rayon_atome,
        couleur="red"
    )


    # ========================================================
    # AXES
    # ========================================================

    ajouter_axes(
        plotter
    )


    # ========================================================
    # AFFICHAGE
    # ========================================================

    plotter.show(  # On affiche la scène 3D
        title="TDE Ge"
    )


# ============================================================
# LANCEMENT DU PROGRAMME
# ============================================================

if __name__ == "__main__":
    main()
