import numpy as np
from typing import List, Dict, Tuple, Optional
from .modeles import Jeu

class AnalyseurJeu:
    def __init__(self, jeu: Jeu):
        self.jeu = jeu
        
    def strategies_dominantes(self, id_joueur: int, faiblement=False) -> List[int]:
        """Version finale corrigée avec vérification précise de la dominance"""
        if id_joueur == 1:
            gains = self.jeu.gains[1]  # Matrice [strat_j1, strat_j2]
            n_strategies = gains.shape[0]
            compare_axis = 1  # On compare les lignes entre elles
        else:
            gains = self.jeu.gains[2]  # Matrice [strat_j1, strat_j2]
            n_strategies = gains.shape[1]
            compare_axis = 0  # On compare les colonnes entre elles
        
        dominantes = []
        
        for strat in range(n_strategies):
            est_dominante = True
            strictement_superieure = True
            
            # Extraire les gains pour cette stratégie
            if id_joueur == 1:
                gains_strat = gains[strat, :]
            else:
                gains_strat = gains[:, strat]
            
            for autre_strat in range(n_strategies):
                if strat == autre_strat:
                    continue
                    
                # Extraire les gains pour l'autre stratégie
                if id_joueur == 1:
                    gains_autre = gains[autre_strat, :]
                else:
                    gains_autre = gains[:, autre_strat]
                
                # Vérifier la dominance
                if not np.all(gains_strat >= gains_autre):
                    est_dominante = False
                    break
                    
                if not np.all(gains_strat > gains_autre):
                    strictement_superieure = False
            
            if est_dominante:
                if not faiblement and strictement_superieure:
                    dominantes.append(strat)
                elif faiblement:
                    dominantes.append(strat)
        
        return dominantes
    
    def elimination_strategies_dominantes(self, strict=True) -> List[Tuple[int]]:
        """
        Élimination itérée des stratégies dominées (corrigé)
        """
        strategies_actives = {
            1: list(range(len(self.jeu.joueurs[0].strategies))),
            2: list(range(len(self.jeu.joueurs[1].strategies)))
        }
        
        while True:
            elimine = False
            
            for joueur in [1, 2]:
                dominantes = self.strategies_dominantes(joueur, faiblement=not strict)
                if dominantes and len(strategies_actives[joueur]) > 1:
                    strategies_actives[joueur] = dominantes
                    elimine = True
            
            if not elimine:
                break
                
        # Générer les profils restants
        from itertools import product
        return list(product(strategies_actives[1], strategies_actives[2]))
    
    def equilibre_nash(self) -> List[Tuple[int, int]]:
        """
        Équilibre de Nash (corrigé)
        """
        equilibres = []
        n_strat_j1 = len(self.jeu.joueurs[0].strategies)
        n_strat_j2 = len(self.jeu.joueurs[1].strategies)
        
        for i in range(n_strat_j1):
            for j in range(n_strat_j2):
                # Vérification pour le joueur 1
                gain_j1 = self.jeu.gains[1][i, j]
                meilleur_j1 = True
                for k in range(n_strat_j1):
                    if self.jeu.gains[1][k, j] > gain_j1:
                        meilleur_j1 = False
                        break
                
                # Vérification pour le joueur 2
                gain_j2 = self.jeu.gains[2][i, j]
                meilleur_j2 = True
                for l in range(n_strat_j2):
                    if self.jeu.gains[2][i, l] > gain_j2:
                        meilleur_j2 = False
                        break
                
                if meilleur_j1 and meilleur_j2:
                    equilibres.append((i, j))
        
        return equilibres
    
    def optimum_pareto(self) -> List[Tuple[int, int]]:
        """
        Optimum de Pareto (corrigé)
        """
        pareto_optima = []
        n_strat_j1 = len(self.jeu.joueurs[0].strategies)
        n_strat_j2 = len(self.jeu.joueurs[1].strategies)
        
        # Générer tous les profils possibles
        profils = [(i, j) for i in range(n_strat_j1) for j in range(n_strat_j2)]
        
        for profil in profils:
            est_pareto = True
            gain_j1 = self.jeu.gains[1][profil]
            gain_j2 = self.jeu.gains[2][profil]
            
            for autre in profils:
                autre_j1 = self.jeu.gains[1][autre]
                autre_j2 = self.jeu.gains[2][autre]
                
                # Vérifier si 'autre' domine 'profil'
                if (autre_j1 >= gain_j1 and autre_j2 >= gain_j2 and 
                    (autre_j1 > gain_j1 or autre_j2 > gain_j2)):
                    est_pareto = False
                    break
            
            if est_pareto:
                pareto_optima.append(profil)
        
        return pareto_optima
    
    def niveau_securite(self, id_joueur: int) -> Tuple[float, int]:
        """
        Niveau de sécurité (corrigé)
        """
        if id_joueur == 1:
            gains = self.jeu.gains[1]
            min_gains = np.min(gains, axis=1)  # Minimum par ligne (stratégie J1)
        else:
            gains = self.jeu.gains[2]
            min_gains = np.min(gains, axis=0)  # Minimum par colonne (stratégie J2)
        
        max_min = np.max(min_gains)
        meilleure_strat = np.argmax(min_gains)
        
        return (max_min, meilleure_strat)