import numpy as np
from typing import List, Dict, Tuple, Optional
from .modeles import Jeu

class AnalyseurJeu:
    def __init__(self, jeu: Jeu):
        self.jeu = jeu
        
    def strategies_dominantes(self, id_joueur: int, faiblement=False) -> List[int]:
        """
        Identifie les stratégies dominantes pour un joueur
        faiblement: Si True, cherche les stratégies faiblement dominantes
        Retourne la liste des indices de stratégies dominantes
        """
        gains = self.jeu.gains[id_joueur]
        n_strategies = gains.shape[0]
        dominantes = []
        
        for i in range(n_strategies):
            dominante = True
            for j in range(n_strategies):
                if i == j:
                    continue
                
                if faiblement:
                    condition = np.all(gains[i] >= gains[j]) and np.any(gains[i] > gains[j])
                else:
                    condition = np.all(gains[i] > gains[j])
                
                if not condition:
                    dominante = False
                    break
                    
            if dominante:
                dominantes.append(i)
                
        return dominantes
    
    def elimination_strategies_dominantes(self, strict=True) -> List[Tuple[int]]:
        """
        Effectue l'élimination itérée des stratégies dominées
        strict: Si True, élimine les stratégies strictement dominées
        Retourne les profils de stratégies survivantes
        """
        joueurs_actifs = self.jeu.joueurs.copy()
        strategies_actives = {j.id: list(range(j.n_strategies)) for j in joueurs_actifs}
        
        while True:
            elimine = False
            
            for j in joueurs_actifs:
                dominantes = self.strategies_dominantes(j.id, faiblement=not strict)
                if dominantes:
                    strategies_actives[j.id] = dominantes
                    elimine = True
            
            if not elimine:
                break
                
        # Générer tous les profils possibles avec les stratégies restantes
        from itertools import product
        profils = list(product(*[strategies_actives[j.id] for j in joueurs_actifs]))
        return profils
    
    def equilibre_nash(self) -> List[Tuple[int]]:
        """
        Trouve tous les équilibres de Nash en stratégies pures
        Retourne une liste de tuples représentant les profils de stratégies
        """
        equilibres = []
        shapes = [j.n_strategies for j in self.jeu.joueurs]
        
        # Générer tous les profils possibles
        from itertools import product
        for profil in product(*[range(s) for s in shapes]):
            est_equilibre = True
            
            for j in self.jeu.joueurs:
                gain_courant = self._obtenir_gain(j.id, profil)
                
                # Tester toutes les déviations possibles
                for s in range(shapes[j.id-1]):
                    if s == profil[j.id-1]:
                        continue
                    
                    nouveau_profil = list(profil)
                    nouveau_profil[j.id-1] = s
                    nouveau_gain = self._obtenir_gain(j.id, nouveau_profil)
                    
                    if nouveau_gain > gain_courant:
                        est_equilibre = False
                        break
                
                if not est_equilibre:
                    break
            
            if est_equilibre:
                equilibres.append(profil)
                
        return equilibres
    
    def _obtenir_gain(self, id_joueur: int, profil: Tuple[int]) -> float:
        """
        Helper function pour extraire le gain d'un joueur donné un profil de stratégies
        """
        return self.jeu.gains[id_joueur][tuple([p-1 if i+1 == id_joueur else p for i, p in enumerate(profil)])]
    
    def optimum_pareto(self) -> List[Tuple[int]]:
        """
        Identifie les optima de Pareto
        Retourne la liste des profils Pareto-optimaux
        """
        shapes = [j.n_strategies for j in self.jeu.joueurs]
        from itertools import product
        tous_profils = list(product(*[range(s) for s in shapes]))
        
        pareto_optima = []
        
        for profil in tous_profils:
            pareto_optimal = True
            gains_profil = [self._obtenir_gain(j.id, profil) for j in self.jeu.joueurs]
            
            for autre_profil in tous_profils:
                if autre_profil == profil:
                    continue
                    
                gains_autre = [self._obtenir_gain(j.id, autre_profil) for j in self.jeu.joueurs]
                
                # Vérifier si autre_profil domine profil
                tous_meilleurs_ou_egaux = all(g >= p for g, p in zip(gains_autre, gains_profil))
                au_moins_un_meilleur = any(g > p for g, p in zip(gains_autre, gains_profil))
                
                if tous_meilleurs_ou_egaux and au_moins_un_meilleur:
                    pareto_optimal = False
                    break
            
            if pareto_optimal:
                pareto_optima.append(profil)
                
        return pareto_optima
    
    def niveau_securite(self, id_joueur: int) -> Tuple[float, int]:
        """
        Calcule le niveau de sécurité pour un joueur
        Retourne (valeur, indice_strategie)
        """
        gains = self.jeu.gains[id_joueur]
        max_min = -np.inf
        meilleure_strat = -1
        
        for i in range(gains.shape[0]):
            min_gain = np.min(gains[i])
            if min_gain > max_min:
                max_min = min_gain
                meilleure_strat = i
                
        return (max_min, meilleure_strat)