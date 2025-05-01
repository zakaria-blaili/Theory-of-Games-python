import streamlit as st
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from itertools import product

# Set absolute path to project root
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from core.modeles import Jeu, Joueur
from core.algorithems import AnalyseurJeu
from core.utils import charger_jeu_classique, normaliser_gains

def creer_jeu_personnalise():
    st.header("🎮 Configuration du Jeu Personnalisé")
    
    # Nombre de joueurs (de 2 à 5)
    num_players = st.selectbox(
        "Nombre de joueurs",
        [2, 3, 4, 5],
        index=0
    )
    
    # Configuration des stratégies pour chaque joueur
    strategies = {}
    for i in range(1, num_players + 1):
        with st.expander(f"Joueur {i} - Configuration", expanded=True):
            strat_count = st.number_input(
                f"Nombre de stratégies pour le Joueur {i}",
                min_value=2,
                max_value=5,
                value=2,
                key=f"strat_joueur_{i}"
            )
            # Let user name each strategy
            strategies[i] = [
                st.text_input(
                    f"Nom stratégie {j+1} (Joueur {i})",
                    value=f"S{j+1}",
                    key=f"strat_name_{i}_{j}"
                )
                for j in range(strat_count)
            ]
    
    # Configuration des gains (using dynamic ND-arrays)
    st.subheader("Matrices des Gains")
    gains = {}
    
    # Create all possible strategy combinations
    all_strat_combinations = list(product(*[range(len(s)) for s in strategies.values()]))
    
    for player_id in range(1, num_players + 1):
        st.markdown(f"**Joueur {player_id}**")
        
        # Initialize ND-array for this player's gains
        shape = tuple(len(s) for s in strategies.values())
        player_gains = np.zeros(shape)
        
        for combo in all_strat_combinations:
            # Create readable label
            combo_label = " / ".join(
                f"{strategies[p+1][s]}" 
                for p, s in enumerate(combo)
            )
            
            # Input for this specific combination
            player_gains[combo] = st.number_input(
                f"Gain J{player_id} quand {combo_label}",
                value=0,
                key=f"gain_{player_id}_{'_'.join(map(str, combo))}"
            )
        
        gains[player_id] = player_gains
    
    # Create players and game
    joueurs = [Joueur(i, strategies[i]) for i in range(1, num_players + 1)]
    
    try:
        return Jeu(joueurs, gains)
    except ValueError as e:
        st.error(f"Erreur de configuration: {str(e)}")
        return None

def display_payoff_matrices(jeu):
    """Display payoff matrices in a user-friendly way"""
    st.subheader("Matrices de Gains")
    
    # For 2-player games, show side-by-side matrices
    if len(jeu.joueurs) == 2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Joueur 1**")
            df1 = pd.DataFrame(
                jeu.gains[1],
                index=[s for s in jeu.joueurs[0].strategies],
                columns=[s for s in jeu.joueurs[1].strategies]
            )
            st.dataframe(df1.style.format("{:.1f}"))
        
        with col2:
            st.markdown(f"**Joueur 2**")
            df2 = pd.DataFrame(
                jeu.gains[2],
                index=[s for s in jeu.joueurs[0].strategies],
                columns=[s for s in jeu.joueurs[1].strategies]
            )
            st.dataframe(df2.style.format("{:.1f}"))
    else:
        # For N-player games, show each player's payoff structure
        for player in jeu.joueurs:
            with st.expander(f"Gains du Joueur {player.id}", expanded=False):
                st.write(f"Dimensions: {jeu.gains[player.id].shape}")
                st.write("Premières valeurs:")
                st.write(jeu.gains[player.id].take(indices=0, axis=range(len(jeu.joueurs))))

def display_iesds_results(analyseur, jeu):
    """Display results of Iterated Elimination of Strictly Dominated Strategies"""
    with st.expander("Élimination Itérative des Stratégies Strictement Dominées (IESDS)", expanded=True):
        try:
            equilibres_iesds, chemin = analyseur.equilibre_iteratif_dominance_stricte()

            
            if equilibres_iesds:
                st.success("Profils stratégiques restants après élimination itérative:")
                
                # Create a table of results
                results = []
                for eq in equilibres_iesds:
                    result = {
                        "Profil": ", ".join(jeu.joueurs[j].strategies[s] for j, s in enumerate(eq))
                    }
                    for player in jeu.joueurs:
                        result[f"Gain J{player.id}"] = jeu.gains[player.id][eq]
                    results.append(result)
                
                df = pd.DataFrame(results)
                st.dataframe(df.style.highlight_max(axis=0, color=''))
                
                if len(equilibres_iesds) == 1:
                    st.success("Solution unique trouvée par IESDS")
                else:
                    st.warning("Plusieurs profils restants - le jeu n'a pas de solution unique par IESDS")
            else:
                st.error("Toutes les stratégies ont été éliminées - aucun équilibre trouvé")
            if chemin:
                st.markdown("### 🔄 Chemin d'élimination")
                for etape in chemin:
                    st.write(f"- {etape}")
            else:
                st.write("Aucune stratégie éliminée")    
            st.markdown("""
            **Explication:**
            - Les stratégies strictement dominées sont éliminées itérativement
            - L'ordre d'élimination n'affecte pas le résultat final (pour la domination stricte)
            - Les profils restants sont des équilibres potentiels
            """)
                
        except Exception as e:
            st.error(f"Erreur dans l'analyse IESDS: {str(e)}")

# Configuration de la page
st.set_page_config(page_title="Analyse des Jeux Stratégiques", page_icon="🎮", layout="wide")
st.title("📊 Analyse des Jeux Stratégiques")
st.markdown("""
Cette application permet d'analyser les jeux stratégiques en utilisant différents concepts de théorie des jeux.
""")

# Sidebar pour la configuration
with st.sidebar:
    st.header("Configuration du Jeu")
    choix_jeu = st.selectbox(
        "Choisir un jeu",
        ["dilemme_prisonnier", "bataille_sexes", "personnalise"],
        index=0
    )
    
    st.markdown("---")
    st.header("Options d'Analyse")
    analyse_nash = st.checkbox("Équilibre de Nash", True)
    analyse_pareto = st.checkbox("Optimum de Pareto", True)
    analyse_securite = st.checkbox("Niveaux de Sécurité", True)
    analyse_dominance = st.checkbox("Stratégies Dominantes", True)
    analyse_iesds = st.checkbox("Élimination Itérative des Stratégies Dominées", True)

# Chargement du jeu
try:
    if choix_jeu == "personnalise":
        jeu = creer_jeu_personnalise()
    else:
        jeu = charger_jeu_classique(choix_jeu)
    
    if jeu:
        analyseur = AnalyseurJeu(jeu)
        
        # Affichage des matrices de gains
        display_payoff_matrices(jeu)
        
        # Affichage des résultats
        st.subheader("Résultats de l'Analyse")
        
        if analyse_nash:
            with st.expander("Équilibre de Nash", expanded=True):
                equilibres = analyseur.equilibre_nash()
                if equilibres:
                    st.write("Équilibres trouvés:")
                    for eq in equilibres:
                        noms = [jeu.joueurs[j].strategies[s] for j, s in enumerate(eq)]
                        st.write(f"- Profil stratégique: {', '.join(noms)}")
                        st.write(f"  Gains correspondants:")
                        for player in jeu.joueurs:
                            st.write(f"  Joueur {player.id}: {jeu.gains[player.id][eq]}")
                else:
                    st.warning("Aucun équilibre de Nash en stratégies pures trouvé")
        
        if analyse_pareto:
            with st.expander("Optimum de Pareto", expanded=True):
                pareto_optima = analyseur.optimum_pareto()
                if pareto_optima:
                    st.write("Optima de Pareto trouvés:")
                    for opt in pareto_optima:
                        noms = [jeu.joueurs[j].strategies[s] for j, s in enumerate(opt)]
                        st.write(f"- Profil stratégique: {', '.join(noms)}")
                        st.write(f"  Gains correspondants:")
                        for player in jeu.joueurs:
                            st.write(f"  Joueur {player.id}: {jeu.gains[player.id][opt]}")
                else:
                    st.warning("Aucun optimum de Pareto trouvé")
        
        if analyse_securite:
            with st.expander("Niveaux de Sécurité", expanded=True):
                for player in jeu.joueurs:
                    valeur, strat = analyseur.niveau_securite(player.id)
                    st.write(f"**Joueur {player.id}**:")
                    st.write(f"- Stratégie de sécurité: {player.strategies[strat]}")
                    st.write(f"- Gain garanti: {valeur:.2f}")
                    st.write("---")
        
        if analyse_dominance:
            with st.expander("Stratégies Dominantes", expanded=True):
                for player in jeu.joueurs:
                    st.write(f"**Joueur {player.id}**:")
                    dom = analyseur.strategies_dominantes(player.id)
                    
                    if dom['strict']:
                        st.write("- Strictement dominantes:")
                        for s in dom['strict']:
                            st.write(f"  - {player.strategies[s]}")
                    else:
                        st.write("- Pas de stratégie strictement dominante")
                    
                    if dom['weak']:
                        st.write("- Faiblement dominantes:")
                        for s in dom['weak']:
                            st.write(f"  - {player.strategies[s]}")
                    else:
                        st.write("- Pas de stratégie faiblement dominante")
                    
                    st.write("---")
        
        if analyse_iesds:
            display_iesds_results(analyseur, jeu)
        
        # Guide théorique
        with st.expander("Guide Théorique", expanded=False):
            st.markdown("""
            **Concepts clés:**
            
            - **Stratégie dominante**: Meilleure réponse quelle que soit la stratégie des autres
            - **Équilibre de Nash**: Profil où aucun joueur ne peut améliorer son gain en changeant unilatéralement
            - **Optimum de Pareto**: Situation où on ne peut améliorer un joueur sans détériorer un autre
            - **Niveau de sécurité**: Gain maximum qu'un joueur peut garantir quel que soit le comportement des autres
            - **IESDS**: Élimination successive des stratégies strictement dominées
            """)


        st.markdown("""
        ---
        <small style='text-align: center; display: block;'>
        Made with <span style='color: red'>❤️</span> using Streamlit | © 2025 Zakaria And Asma
        </small>
        """, unsafe_allow_html=True)


except Exception as e:
    st.error(f"Une erreur est survenue: {str(e)}")
    st.error("Veuillez vérifier que tous les modules nécessaires sont correctement installés.")