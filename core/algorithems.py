import numpy as np
from typing import List, Dict, Tuple, Optional
from .modeles import Jeu
from itertools import product

class AnalyseurJeu:
    def __init__(self, jeu: Jeu):
        self.jeu = jeu
        
    def strategies_dominantes(self, id_joueur: int) -> Dict[str, List[int]]:
        """
        Returns dominant strategies categorized properly.
        Returns: {
            'strict': [indices of strictly dominant strategies],
            'weak': [indices of weakly (but not strictly) dominant strategies]
        }
        """
        gains = self.jeu.gains[id_joueur]
        n_strategies = len(self.jeu.joueurs[id_joueur-1].strategies)
        result = {'strict': set(), 'weak': set()}

        # Compare all strategy pairs
        for strat in range(n_strategies):
            strictly_dominates_any = False
            weakly_dominates_any = False
            
            for other in range(n_strategies):
                if strat == other:
                    continue
                    
                if id_joueur == 1:
                    diff = gains[strat, :] - gains[other, :]
                else:
                    diff = gains[:, strat] - gains[:, other]
                
                # Check strict dominance
                if np.all(diff > 0):
                    strictly_dominates_any = True
                    break  # No need to check others if strictly dominates one
                    
                # Check weak dominance if not already found strict
                if np.all(diff >= 0) and np.any(diff > 0):
                    weakly_dominates_any = True
            
            # Categorize the strategy
            if strictly_dominates_any:
                result['strict'].add(strat)
            elif weakly_dominates_any:
                result['weak'].add(strat)
        
        # Convert sets to sorted lists
        return {k: sorted(v) for k, v in result.items()}
    
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
                
        return list(product(*[strategies_actives[j.id] for j in self.jeu.joueurs]))
    
    def equilibre_nash(self):
        """N-player Nash equilibrium"""
        shapes = [len(j.strategies) for j in self.jeu.joueurs]
        equilibres = []
        
        for profil in product(*[range(s) for s in shapes]):
            is_equilibrium = True
            for i, joueur in enumerate(self.jeu.joueurs):
                current_payoff = self.jeu.gains[joueur.id][profil]
                for dev in range(shapes[i]):
                    if dev == profil[i]:
                        continue
                    new_profil = list(profil)
                    new_profil[i] = dev
                    if self.jeu.gains[joueur.id][tuple(new_profil)] > current_payoff:
                        is_equilibrium = False
                        break
                if not is_equilibrium:
                    break
            if is_equilibrium:
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