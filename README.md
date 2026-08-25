# Automatisation de campagnes de calcul de TDE sur LAMMPS

Scripts Python développés dans le cadre d'un stage au **LAAS-CNRS** pour automatiser des campagnes de simulations atomistiques avec **LAMMPS**, dans le but d'étudier l'énergie de seuil dans le germanium (Ge).

Les simulations utilisent un **potentiel interatomique basé sur le machine learning**.

## Objectif

L'objectif de ce projet est d'étudier l'**énergie de seuil** (*Threshold Displacement Energy*, TDE) dans le germanium.

Pour cela, des campagnes de simulations sont réalisées pour différentes **directions** et différentes **énergies**. Les résultats sont ensuite analysés afin de déterminer si une **paire de Frenkel** a été créée ou non.

Une paire de Frenkel correspond à la présence simultanée d'une **lacune** et d'un **interstitiel** dans le matériau à la suite du déplacement d'un atome.

## Fonctionnement

La campagne de simulations est organisée en plusieurs étapes :

1. Génération de l'arborescence et des fichiers nécessaires aux simulations.
2. Lancement des calculs LAMMPS.
3. Attente de la fin des calculs.
4. Analyse des résultats pour déterminer la présence ou non d'une paire de Frenkel.
5. Sélection des directions nécessitant des simulations supplémentaires.
6. Augmentation de l'énergie et répétition du processus.

Le script `search_TDE.py` automatise l'ensemble de cette procédure.

## Organisation des scripts

Les scripts du projet peuvent être regroupés en deux catégories :

### Recherche de l'énergie de seuil

* `generate_TDE.py` : préparation de la campagne de simulations ;
* `launch_TDE.py` : lancement des calculs ;
* `detect_TDE.py` : analyse des simulations et détection des paires de Frenkel ;
* `search_TDE.py` : automatisation de l'ensemble de la campagne.

### Analyse et visualisation

* `plot_TDE_histogramme.py` : visualisation de la distribution des énergies de seuil ;
* `plot_TDE_proba.py` : calcul et visualisation de la probabilité de création d'une paire de Frenkel en fonction de l'énergie ;
* `map_3D_TDE.py` : visualisation des TDE en fonction des directions.

Les scripts d'analyse utilisent les données contenues dans le fichier `TDE_results.txt` généré à la fin d'une campagne par le script search_TDE.py.

## Scripts pour la campagne de calcul de TDE

### `generate_TDE.py`

Ce script prépare une campagne de simulations.

Il permet notamment de :

* créer l'arborescence des dossiers ;
* générer les fichiers d'entrée nécessaires aux simulations LAMMPS ;
* créer les fichiers batch permettant de lancer les calculs.

Il constitue la première étape de la campagne.

### `launch_TDE.py`

Ce script permet de lancer les calculs associés aux fichiers batch générés précédemment.

### `detect_TDE.py`

Ce script analyse les résultats des simulations.

Son objectif principal est de déterminer si une **paire de Frenkel** a été créée au cours de la simulation.

Il permet ainsi de déterminer, pour une direction et une énergie données, si le déplacement produit un défaut permanent dans le matériau.

### `search_TDE.py`

Ce script automatise l'ensemble de la campagne de recherche de l'énergie de seuil.

Il utilise les trois autres scripts :

À partir d'un ensemble de **directions** et d'une **énergie initiale**, `search_TDE.py` :

1. lance `generate_TDE.py` afin de créer l'arborescence et les fichiers nécessaires ;
2. lance `launch_TDE.py` afin de démarrer les calculs ;
3. attend la fin des simulations ;
4. utilise `detect_TDE.py` pour analyser les résultats ;
5. conserve les directions pour lesquelles l'énergie de seuil n'a pas encore été déterminée ;
6. augmente l'énergie ;
7. recommence la campagne avec les directions restantes.

Cette automatisation permet de rechercher l'énergie de seuil pour différentes directions sans avoir à lancer manuellement chaque étape.

## Scripts pour l'analyse des résultats

À la fin d'une campagne de recherche, le script `search_TDE.py` génère un fichier `TDE_results.txt` contenant les résultats obtenus pour les différentes directions simulées.

Ce fichier permet ensuite d'analyser les résultats de la campagne et de visualiser la distribution de l'énergie de seuil.

Plusieurs scripts Python ont été développés pour faciliter cette analyse.

### plot_TDE_histogramme.py

Le premier script permet de représenter les résultats sous forme d'un **histogramme**.

Cette représentation permet notamment de visualiser la distribution des énergies de seuil obtenues au cours de la campagne de simulations.

### plot_TDE_proba.py

Le deuxième script permet de calculer et de représenter la **probabilité de création d'une paire de Frenkel en fonction de l'énergie**.

Cette représentation permet d'étudier l'évolution de la probabilité de création d'un défaut en fonction de l'énergie incidente.

### map_3D_TDE.py

Le troisième script permet de représenter les résultats sous la forme d'une **carte 3D de l'énergie de seuil**.

Les directions sont représentées dans l'espace et les couleurs indiquent la valeur de l'énergie de seuil associée à chaque direction.

Cette représentation permet de visualiser la dépendance directionnelle de l'énergie de seuil dans le germanium.

## Structure du projet

```text
.
├── README.md
├── src/
│   ├── generate_TDE.py
│   ├── launch_TDE.py
│   ├── detect_TDE.py
│   └── search_TDE.py
│   └── plot_TDE_histogramme.py
│   └── plot_TDE_proba.py
│   └── map_3D_TDE.py
├── examples/
├── docs/
└── tests/
```

### `src/`

Contient les scripts Python principaux du projet.

### `examples/`

Contient des exemples d'utilisation des scripts et de lancement de campagnes de simulations.

### `docs/`

Contient la documentation détaillée du projet.

### `tests/`

Contient les tests permettant de vérifier le fonctionnement des différents scripts.

## Utilisation

A remplir





## Prérequis

Le projet utilise notamment :

* Python
* LAMMPS
* un potentiel interatomique basé sur le machine learning
* etc ... (voir autres, notamment les inputs)



## Documentation

La documentation détaillée du projet est disponible dans le dossier [`docs/`](docs/).

Elle décrira notamment :

* les paramètres des scripts ;
* la préparation d'une campagne ;
* le fonctionnement des simulations LAMMPS ;
* l'analyse des résultats ;
* la détection des paires de Frenkel ;
* la méthode de recherche de l'énergie de seuil.

## Contexte

Ce projet a été développé dans le cadre d'un stage au **LAAS-CNRS** portant sur l'étude de l'énergie de seuil dans le germanium.

## Auteur

**[Alexandre THOMAS]**

Stage au LAAS-CNRS
