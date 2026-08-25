import numpy as np
import matplotlib.pyplot as plt

# Lire les énergies TDE
E = []

with open("TDE_results.txt", "r") as f:
    for line in f:
        parts = line.split()   # découpe la ligne en fonction des espaces.

        # Une ligne valide contient : direction, énergie, eV
        if len(parts) == 3 and parts[2] == "eV":  # garde la ligne que si elle possède exactement trois éléments et que le troisième est "eV"
            E.append(float(parts[1])) # récupère l'énergie

E = np.array(E)

# Vérification
print("Nombre de directions :", len(E))
print("Énergies :", np.sort(E))

# Énergies distinctes et nombre de directions pour chaque énergie
energies, counts = np.unique(E, return_counts=True)  # energies contient les valeurs différentes contenues dans E et counts c'est le nombre de fois ou elles apparaissent

# Probabilité cumulée
P = np.cumsum(counts) / len(E) #cumsum = somme cumulée donc P devient un tableau : [a1 , a1+a2, a1+a2+a3]; ça donne donc  P= somme des val <= val_actuelle / nbr total de val

# Tracé
plt.step(energies, P, where="post")  # dessine la courbe en escalier
plt.scatter(energies, P, s=40)   # ajoute les points sur la courbe

plt.xlabel("Énergie seuil de déplacement (eV)")
plt.ylabel("Probabilité cumulée de création d'une paire de Frenkel")

plt.xlim(0, 40)
plt.ylim(0, 1.05)

plt.grid(True, linestyle="--", alpha=0.6) # Pour afficher des grilles sur le graphe
plt.tight_layout() # Pour afficher les titres proprement
plt.show()
