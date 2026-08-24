# Recherche de l'énergie de seuil dans le germanium

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

## Scripts

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

## Structure du projet

```text
.
├── README.md
├── src/
│   ├── generate_TDE.py
│   ├── launch_TDE.py
│   ├── detect_TDE.py
│   └── search_TDE.py
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

**[Prénom Nom]**

Stage au LAAS-CNRS
