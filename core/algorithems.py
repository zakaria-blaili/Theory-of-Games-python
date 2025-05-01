import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from .modeles import Jeu
from itertools import product

class AnalyseurJeu:
    def __init__(self, jeu: Jeu):
        self.jeu = jeu
        
    def strategies_dominantes(self, id_joueur: int) -> Dict[str, List[int]]:
        """
        Retourne les stratégies strictement et faiblement dominantes.
        """
        strict = self._strategies_dominantes_type(id_joueur, faiblement=False)
        weak = self._strategies_dominantes_type(id_joueur, faiblement=True)
        return {
            "strict": strict,
            "weak": weak
        }

    def _strategies_dominantes_type(self, id_joueur: int, faiblement: bool) -> List[int]:
        player_idx = id_joueur - 1
        gains = self.jeu.gains[id_joueur]
        n_strategies = len(self.jeu.joueurs[player_idx].strategies)
        dominantes = []

        for strat in range(n_strategies):
            is_dominated = False
            for other in range(n_strategies):
                if strat == other:
                    continue

                # Build mask for all other players’ strategies
                others = [list(range(len(j.strategies))) for j in self.jeu.joueurs if j.id != id_joueur]
                for combi in product(*others):
                    if id_joueur == 1:
                        strat_payoff = gains[(strat,) + combi]
                        other_payoff = gains[(other,) + combi]
                    else:
                        strat_payoff = gains[combi[:id_joueur-1] + (strat,) + combi[id_joueur-1:]]
                        other_payoff = gains[combi[:id_joueur-1] + (other,) + combi[id_joueur-1:]]

                    if not faiblement and strat_payoff >= other_payoff:
                        break
                    if faiblement and strat_payoff > other_payoff:
                        break
                else:
                    # All comparisons passed (domination)
                    dominantes.append(strat)

        return dominantes


    
    def est_strictement_dominee(self, id_joueur: int, strat: int, strategies_actives: Dict[int, List[int]]) -> bool:
        """
        Vérifie si une stratégie est strictement dominée.
        """
        gains = self.jeu.gains[id_joueur]
        player_idx = id_joueur - 1
        
        for other in strategies_actives[id_joueur]:
            if other == strat:
                continue
                
            if id_joueur == 1:
                # For player 1, compare rows
                opponent_id = 2
                mask = [i in strategies_actives[opponent_id] for i in range(gains.shape[1])]
                diff = gains[strat, :][mask] - gains[other, :][mask]
            else:
                # For player 2, compare columns
                opponent_id = 1
                mask = [i in strategies_actives[opponent_id] for i in range(gains.shape[0])]
                diff = gains[:, strat][mask] - gains[:, other][mask]
            
            if np.all(diff < 0):
                return True
                
        return False
    
    def elimination_strategies_dominantes(self, strict: bool = True) -> List[Tuple[int, ...]]:
        """
        Élimination itérée des stratégies dominées.
        """
        # Initialize active strategies (convert to 1-based IDs)
        strategies_actives = {
            joueur.id: list(range(len(joueur.strategies)))
            for joueur in self.jeu.joueurs
        }
        
        changed = True
        while changed:
            changed = False
            
            for joueur in self.jeu.joueurs:
                to_remove = []
                for strat in strategies_actives[joueur.id]:
                    if self.est_strictement_dominee(joueur.id, strat, strategies_actives):
                        to_remove.append(strat)
                        changed = True
                
                if to_remove:
                    strategies_actives[joueur.id] = [
                        s for s in strategies_actives[joueur.id] 
                        if s not in to_remove
                    ]
        
        # Generate remaining strategy profiles
        return list(product(*[
            strategies_actives[joueur.id] 
            for joueur in sorted(self.jeu.joueurs, key=lambda x: x.id)
        ]))
    
    def equilibre_iteratif_dominance_stricte(self) -> Tuple[List[Tuple[int]], List[str]]:
        """
        Retourne les profils restants et le chemin d'élimination (sous forme de texte lisible).
        """
        joueurs = self.jeu.joueurs
        gains = self.jeu.gains
        strategies_actives = {j.id: set(range(len(j.strategies))) for j in joueurs}
        
        chemin_elimination = []
        modification = True
        
        while modification:
            modification = False
            for joueur in joueurs:
                id_j = joueur.id
                actives = list(strategies_actives[id_j])
                for strat in actives:
                    if self.est_strictement_dominee(id_j, strat, strategies_actives):
                        strategies_actives[id_j].remove(strat)
                        chemin_elimination.append(f"Joueur {id_j} : stratégie éliminée -> {joueur.strategies[strat]}")
                        modification = True
                        break  # recommencer l'itération si on a supprimé une stratégie
                if modification:
                    break

        # Générer tous les profils restants
        restants = list(product(*[list(strategies_actives[j.id]) for j in joueurs]))
        return restants, chemin_elimination

    
    def equilibre_nash(self) -> List[Tuple[int, ...]]:
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
        """Optimum de Pareto"""
        shapes = [len(j.strategies) for j in self.jeu.joueurs]
        pareto_optima = []
        tous_profils = list(product(*[range(s) for s in shapes]))
        
        for profil in tous_profils:
            est_pareto = True
            gains_profil = [self.jeu.gains[j.id][profil] for j in self.jeu.joueurs]
            
            for autre in tous_profils:
                if autre == profil:
                    continue
                    
                gains_autre = [self.jeu.gains[j.id][autre] for j in self.jeu.joueurs]
                
                if all(g >= p for g, p in zip(gains_autre, gains_profil)) and \
                   any(g > p for g, p in zip(gains_autre, gains_profil)):
                    est_pareto = False
                    break
            
            if est_pareto:
                pareto_optima.append(profil)
        
        return pareto_optima
    
    def niveau_securite(self, id_joueur: int) -> Tuple[float, int]:
        """Niveau de sécurité pour un joueur"""
        gains = self.jeu.gains[id_joueur]
        player_idx = id_joueur - 1
        n_strategies = len(self.jeu.joueurs[player_idx].strategies)
        
        if id_joueur == 1:
            min_gains = np.min(gains, axis=1)  # Minimum par ligne
        else:
            min_gains = np.min(gains, axis=0)  # Minimum par colonne
        
        max_min = np.max(min_gains)
        meilleure_strat = np.argmax(min_gains)
        
        return (max_min, meilleure_strat)
    
    def meilleure_reponse(self, id_joueur: int, strategies_autres: Tuple[int, ...]) -> List[int]:
        """Meilleure réponse pour un joueur"""
        gains = self.jeu.gains[id_joueur]
        player_idx = id_joueur - 1
        n_strategies = len(self.jeu.joueurs[player_idx].strategies)
        
        # Rebuild complete index
        index = list(strategies_autres)
        index.insert(player_idx, 0)  # Temporary value
        
        meilleures = []
        max_gain = -np.inf
        
        for strat in range(n_strategies):
            index[player_idx] = strat
            gain = gains[tuple(index)]
            
            if gain > max_gain:
                max_gain = gain
                meilleures = [strat]
            elif gain == max_gain:
                meilleures.append(strat)
        
        return meilleures