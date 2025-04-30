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
        self.joueurs = joueurs
        self.gains = gains
        self._valider_matrice_gains()  # Ajout de la validation
        
    def _valider_matrice_gains(self):
        """Vérifie que les matrices ont les bonnes dimensions"""
        expected_shape = [len(j.strategies) for j in self.joueurs]
        
        for j in self.joueurs:
            mat = self.gains[j.id]
            if mat.shape != tuple(expected_shape):
                raise ValueError(
                    f"Dimensions incorrectes pour le joueur {j.id}. "
                    f"Attendu: {expected_shape}, Reçu: {mat.shape}"
                )
    
    def get_strategie_name(self, id_joueur: int, index: int) -> str:
        """Retourne le nom d'une stratégie"""
        for j in self.joueurs:
            if j.id == id_joueur:
                return j.strategies[index]
        raise ValueError("Joueur non trouvé")
    


    def __repr__(self):
        return f"Jeu à {self.n_joueurs} joueurs"