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


# Histogramme
plt.bar(energies, counts)

plt.xlabel("Énergie seuil de déplacement (eV)")
plt.ylabel("Nombre d'occurrences")
plt.title("Histogramme de la campagne TDE : Nombre d'occurence de l'énergie pour 207 directions")


plt.xlim(0, 40)


plt.grid(True, linestyle="--", alpha=0.6) # Pour afficher des grilles sur le graphe
plt.tight_layout() # Pour afficher les titres proprement
plt.show()
