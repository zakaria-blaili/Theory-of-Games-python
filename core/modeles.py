from typing import List, Dict, Tuple
import numpy as np

class Joueur:
    def __init__(self, id_joueur: int, strategies: List[str]):
        self.id = id_joueur
        self.strategies = strategies
        self.n_strategies = len(strategies)
        
    def __repr__(self):
        return f"Joueur {self.id} ({self.n_strategies} stratégies)"

class Jeu:
    def __init__(self, joueurs: List[Joueur], gains: Dict[int, np.ndarray]):
        """
        joueurs: Liste des joueurs
        gains: Dictionnaire {id_joueur: matrice_des_gains}
               où matrice_des_gains est de forme (n_strategies_joueur, *n_strategies_autres)
        """
        self.joueurs = joueurs
        self.n_joueurs = len(joueurs)
        self.gains = gains
        
        # Vérifier la cohérence des dimensions
        self._valider_matrice_gains()
        
def _valider_matrice_gains(self):
    """Vérifie que les matrices de gains ont des dimensions compatibles
    avec le nombre de stratégies de chaque joueur"""
    # Vérifier que chaque matrice a le bon nombre de dimensions
    for j in self.joueurs:
        mat = self.gains[j.id]
        if len(mat.shape) != len(self.joueurs):
            raise ValueError(f"La matrice du joueur {j.id} doit avoir {len(self.joueurs)} dimensions")
    
    # Vérifier que les dimensions correspondent aux nombres de stratégies
    expected_shape = []
    for j in self.joueurs:
        expected_shape.append(len(j.strategies))
    
    for j in self.joueurs:
        mat = self.gains[j.id]
        if mat.shape != tuple(expected_shape):
            raise ValueError(
                f"Dimensions incohérentes pour le joueur {j.id}. "
                f"Attendu: {expected_shape}, Reçu: {mat.shape}"
            )

    def get_strategie_name(self, id_joueur: int, index_strategie: int) -> str:
        """Retourne le nom d'une stratégie à partir de son index"""
        for j in self.joueurs:
            if j.id == id_joueur:
                return j.strategies[index_strategie]
        raise ValueError("Joueur non trouvé")

    def __repr__(self):
        return f"Jeu à {self.n_joueurs} joueurs"