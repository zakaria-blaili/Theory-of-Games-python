import numpy as np
from typing import List, Dict, Tuple, Optional
from .modeles import Jeu

class AnalyseurJeu:
    def __init__(self, jeu: Jeu):
        self.jeu = jeu
        
    def strategies_dominantes(self, id_joueur: int, faiblement=False) -> List[int]:
        """
        Identifie les stratégies dominantes pour un joueur donné.
        Compatible avec des nombres de stratégies différents par joueur.
        """
        gains = self.jeu.gains[id_joueur]
        n_strategies = len(self.jeu.joueurs[id_joueur-1].strategies)
        dominantes = []
        
        for strat in range(n_strategies):
            est_dominante = True
            strictement = False
            
            for autre in range(n_strategies):
                if strat == autre:
                    continue
                
                if id_joueur == 1:
                    comp = gains[strat, :] >= gains[autre, :]
                    comp_strict = gains[strat, :] > gains[autre, :]
                else:
                    comp = gains[:, strat] >= gains[:, autre]
                    comp_strict = gains[:, strat] > gains[:, autre]
                
                if not np.all(comp):
                    est_dominante = False
                    break
                    
                if np.all(comp_strict):
                    strictement = True
            
            if est_dominante:
                if not faiblement and strictement:
                    dominantes.append(strat)
                elif faiblement:
                    dominantes.append(strat)
        
        return dominantes
    
    def elimination_strategies_dominantes(self, strict=True) -> List[Tuple[int]]:
        """
        Élimination itérée des stratégies dominées.
        Gère les jeux avec des nombres de stratégies différents.
        """
        strategies_actives = {
            j.id: list(range(len(j.strategies))) 
            for j in self.jeu.joueurs
        }
        
        while True:
            elimine = False
            
            for joueur in self.jeu.joueurs:
                dominantes = self.strategies_dominantes(joueur.id, faiblement=not strict)
                if dominantes and len(strategies_actives[joueur.id]) > 1:
                    strategies_actives[joueur.id] = dominantes
                    elimine = True
            
            if not elimine:
                break
                
        # Générer les profils restants
        from itertools import product
        return list(product(*[strategies_actives[j.id] for j in self.jeu.joueurs]))
    
    def equilibre_nash(self) -> List[Tuple[int, ...]]:
        """
        Équilibre de Nash pour des jeux à N joueurs avec stratégies différentes.
        """
        equilibres = []
        shapes = [len(j.strategies) for j in self.jeu.joueurs]
        
        # Générer tous les profils possibles
        from itertools import product
        tous_profils = product(*[range(s) for s in shapes])
        
        for profil in tous_profils:
            est_equilibre = True
            
            for i, joueur in enumerate(self.jeu.joueurs):
                gain_actuel = self.jeu.gains[joueur.id][profil]
                
                # Vérifier toutes les déviations possibles
                for deviation in range(shapes[i]):
                    if deviation == profil[i]:
                        continue
                        
                    nouveau_profil = list(profil)
                    nouveau_profil[i] = deviation
                    nouveau_profil = tuple(nouveau_profil)
                    
                    if self.jeu.gains[joueur.id][nouveau_profil] > gain_actuel:
                        est_equilibre = False
                        break
                
                if not est_equilibre:
                    break
            
            if est_equilibre:
                equilibres.append(profil)
        
        return equilibres
    
    def optimum_pareto(self) -> List[Tuple[int, ...]]:
        """
        Optimum de Pareto pour des jeux avec stratégies différentes.
        """
        pareto_optima = []
        shapes = [len(j.strategies) for j in self.jeu.joueurs]
        
        # Générer tous les profils possibles
        from itertools import product
        tous_profils = list(product(*[range(s) for s in shapes]))
        
        for profil in tous_profils:
            est_pareto = True
            gains_profil = [self.jeu.gains[j.id][profil] for j in self.jeu.joueurs]
            
            for autre in tous_profils:
                if autre == profil:
                    continue
                    
                gains_autre = [self.jeu.gains[j.id][autre] for j in self.jeu.joueurs]
                
                # Vérifier domination Pareto
                tous_meilleurs_ou_egaux = all(g >= p for g, p in zip(gains_autre, gains_profil))
                au_moins_un_meilleur = any(g > p for g, p in zip(gains_autre, gains_profil))
                
                if tous_meilleurs_ou_egaux and au_moins_un_meilleur:
                    est_pareto = False
                    break
            
            if est_pareto:
                pareto_optima.append(profil)
        
        return pareto_optima
    
    def niveau_securite(self, id_joueur: int) -> Tuple[float, int]:
        """
        Niveau de sécurité pour un joueur avec gestion des dimensions variables.
        """
        gains = self.jeu.gains[id_joueur]
        joueur_index = id_joueur - 1
        n_strategies = len(self.jeu.joueurs[joueur_index].strategies)
        
        if id_joueur == 1:
            min_gains = np.min(gains, axis=1)  # Minimum par ligne
        else:
            min_gains = np.min(gains, axis=0)  # Minimum par colonne
        
        max_min = np.max(min_gains)
        meilleure_strat = np.argmax(min_gains)
        
        return (max_min, meilleure_strat)
    
    def meilleure_reponse(self, id_joueur: int, strategies_autres: Tuple[int, ...]) -> List[int]:
        """
        Trouve les meilleures réponses pour un joueur donné une stratégie des autres.
        """
        gains = self.jeu.gains[id_joueur]
        joueur_index = id_joueur - 1
        n_strategies = len(self.jeu.joueurs[joueur_index].strategies)
        
        # Reconstruire l'index complet
        index = list(strategies_autres)
        index.insert(joueur_index, 0)  # Valeur temporaire
        
        meilleures = []
        max_gain = -np.inf
        
        for strat in range(n_strategies):
            index[joueur_index] = strat
            gain = gains[tuple(index)]
            
            if gain > max_gain:
                max_gain = gain
                meilleures = [strat]
            elif gain == max_gain:
                meilleures.append(strat)
        
        return meilleures