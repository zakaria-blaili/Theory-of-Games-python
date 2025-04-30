import numpy as np
from typing import Dict, List
from core.modeles import Jeu, Joueur 

def creer_jeu_depuis_matrices(gains_joueurs: Dict[int, np.ndarray], noms_strategies: Dict[int, List[str]]) -> Jeu:
    """
    Crée un jeu à partir des matrices de gains et noms de stratégies
    gains_joueurs: {id_joueur: matrice_gains}
    noms_strategies: {id_joueur: [noms_strategies]}
    """
    joueurs = []
    for id_joueur, noms in noms_strategies.items():
        joueurs.append(Joueur(id_joueur, noms))
    
    return Jeu(joueurs, gains_joueurs)

def charger_jeu_classique(nom_jeu: str) -> Jeu:
    """
    Charge un jeu classique prédéfini
    """
    jeux = {
        "dilemme_prisonnier": {
            "joueurs": [1, 2],
            "strategies": {
                1: ["Cooperer", "Trahir"],
                2: ["Cooperer", "Trahir"]
            },
            "gains": {
                1: np.array([[3, 0], [5, 1]]),  # Matrice pour joueur 1
                2: np.array([[3, 5], [0, 1]])   # Matrice pour joueur 2 (transposée)
            }
        },
        "bataille_sexes": {
            "joueurs": [1, 2],
            "strategies": {
                1: ["Football", "Shopping"],
                2: ["Football", "Shopping"]
            },
            "gains": {
                1: np.array([[3, 0], [0, 2]]),
                2: np.array([[2, 0], [0, 3]])
            }
        }
    }
    
    if nom_jeu not in jeux:
        raise ValueError(f"Jeu inconnu: {nom_jeu}")
    
    config = jeux[nom_jeu]
    return creer_jeu_depuis_matrices(config["gains"], config["strategies"])

def normaliser_gains(gains: Dict[int, np.ndarray]) -> Dict[int, np.ndarray]:
    """
    Normalise les gains entre 0 et 1 pour chaque joueur
    """
    normalises = {}
    for joueur, mat in gains.items():
        mat_min = np.min(mat)
        mat_max = np.max(mat)
        if mat_max != mat_min:
            normalises[joueur] = (mat - mat_min) / (mat_max - mat_min)
        else:
            normalises[joueur] = np.ones_like(mat) * 0.5
    return normalises