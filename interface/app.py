import streamlit as st
import sys
from pathlib import Path
import numpy as np

# Set absolute path to project root
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from core.modeles import Jeu, Joueur
from core.algorithems import AnalyseurJeu
from core.utils import charger_jeu_classique, normaliser_gains

def creer_jeu_personnalise():
    st.header("🎮 Configuration du Jeu Personnalisé")
    
    # Nombre de joueurs
    num_players = st.selectbox("Nombre de joueurs", [2], index=0)
    
    # Configuration des stratégies
    strategies = {}
    for i in range(1, num_players + 1):
        strat_count = st.number_input(
            f"Nombre de stratégies pour le Joueur {i}",
            min_value=2,
            max_value=5,
            value=2,
            key=f"strat_joueur_{i}"
        )
        strategies[i] = [f"Stratégie {chr(65+j)}" for j in range(strat_count)]
    
    # Configuration des gains
    st.subheader("Matrices des Gains")
    
    # Pour un jeu à 2 joueurs
    if num_players == 2:
        p1_matrix = np.zeros((len(strategies[1]), len(strategies[2])))
        p2_matrix = np.zeros((len(strategies[1]), len(strategies[2])))
        
        cols = st.columns(2)
        with cols[0]:
            st.write("**Joueur 1**")
            for i in range(len(strategies[1])):
                for j in range(len(strategies[2])):
                    p1_matrix[i,j] = st.number_input(
                        f"J1 gain quand {strategies[1][i]}/{strategies[2][j]}",
                        value=0,
                        key=f"p1_{i}_{j}"
                    )
        
        with cols[1]:
            st.write("**Joueur 2**")
            for i in range(len(strategies[1])):
                for j in range(len(strategies[2])):
                    p2_matrix[i,j] = st.number_input(
                        f"J2 gain quand {strategies[1][i]}/{strategies[2][j]}",
                        value=0,
                        key=f"p2_{i}_{j}"
                    )
        
        # Création des joueurs et du jeu
        joueurs = [
            Joueur(1, strategies[1]),
            Joueur(2, strategies[2])
        ]
        gains = {1: p1_matrix, 2: p2_matrix}
        
        return Jeu(joueurs, gains)
    else:
        st.warning("Seuls les jeux à 2 joueurs sont supportés pour le moment")
        return None

# Configuration de la page
st.set_page_config(page_title="Analyse des Jeux Stratégiques", page_icon="📊", layout="wide")
st.title("📊 Analyse des Jeux Stratégiques")
st.markdown("""
Cette application permet d'analyser les jeux stratégiques à 2 joueurs en utilisant différents concepts de théorie des jeux.
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

# Chargement du jeu
try:
    if choix_jeu == "personnalise":
        jeu = creer_jeu_personnalise()
    else:
        jeu = charger_jeu_classique(choix_jeu)
    
    if jeu:
        analyseur = AnalyseurJeu(jeu)
        
        # Affichage des matrices de gains
        st.subheader("Matrices de Gains")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Joueur 1**")
            # Convert to DataFrame for better display
            import pandas as pd
            df1 = pd.DataFrame(
                jeu.gains[1],
                index=[jeu.get_strategie_name(1, i) for i in range(len(jeu.joueurs[0].strategies))],
                columns=[jeu.get_strategie_name(2, j) for j in range(len(jeu.joueurs[1].strategies))]
            )
            st.dataframe(df1.style.format("{:.1f}"))
        
        with col2:
            st.markdown(f"**Joueur 2**")
            df2 = pd.DataFrame(
                jeu.gains[2],
                index=[jeu.get_strategie_name(1, i) for i in range(len(jeu.joueurs[0].strategies))],
                columns=[jeu.get_strategie_name(2, j) for j in range(len(jeu.joueurs[1].strategies))]
            )
            st.dataframe(df2.style.format("{:.1f}"))
        
        # Affichage des résultats
        st.subheader("Résultats de l'Analyse")
        
        if analyse_nash:
            with st.expander("Équilibre de Nash", expanded=True):
                equilibres = analyseur.equilibre_nash()
                if equilibres:
                    st.write("Équilibres trouvés:")
                    for eq in equilibres:
                        noms = [jeu.get_strategie_name(i+1, s) for i, s in enumerate(eq)]
                        st.write(f"- Profil stratégique: {', '.join(noms)}")
                        st.write(f"  Gains correspondants:")
                        for j, player_id in enumerate(jeu.gains.keys()):
                            st.write(f"  Joueur {player_id}: {jeu.gains[player_id][eq[0], eq[1]]}")
                else:
                    st.warning("Aucun équilibre de Nash en stratégies pures trouvé")
        
        if analyse_pareto:
            with st.expander("Optimum de Pareto", expanded=True):
                pareto_optima = analyseur.optimum_pareto()
                if pareto_optima:
                    st.write("Optima de Pareto trouvés:")
                    for opt in pareto_optima:
                        noms = [jeu.get_strategie_name(i+1, s) for i, s in enumerate(opt)]
                        st.write(f"- Profil stratégique: {', '.join(noms)}")
                        st.write(f"  Gains correspondants:")
                        for j, player_id in enumerate(jeu.gains.keys()):
                            st.write(f"  Joueur {player_id}: {jeu.gains[player_id][opt[0], opt[1]]}")
                else:
                    st.warning("Aucun optimum de Pareto trouvé")
        
        if analyse_securite:
            with st.expander("Niveaux de Sécurité", expanded=True):
                for j in jeu.joueurs:
                    valeur, strat = analyseur.niveau_securite(j.id)
                    st.write(f"**Joueur {j.id}**:")
                    st.write(f"- Stratégie de sécurité: {jeu.get_strategie_name(j.id, strat)}")
                    st.write(f"- Gain garanti: {valeur:.2f}")
                    st.write("---")
        
        if analyse_dominance:
            with st.expander("Stratégies Dominantes", expanded=True):
                for j in jeu.joueurs:
                    st.write(f"**Joueur {j.id}**:")
                    
                    # Strictement dominantes
                    dom_strict = analyseur.strategies_dominantes(j.id, faiblement=False)
                    if dom_strict:
                        st.write("- Strictement dominantes:")
                        for s in dom_strict:
                            st.write(f"  - {jeu.get_strategie_name(j.id, s)}")
                    else:
                        st.write("- Pas de stratégie strictement dominante")
                    
                    # Faiblement dominantes
                    dom_faible = analyseur.strategies_dominantes(j.id, faiblement=True)
                    if dom_faible:
                        st.write("- Faiblement dominantes:")
                        for s in dom_faible:
                            st.write(f"  - {jeu.get_strategie_name(j.id, s)}")
                    else:
                        st.write("- Pas de stratégie faiblement dominante")
                    
                    st.write("---")
        
        # Guide théorique
        with st.expander("Guide Théorique", expanded=False):
            st.markdown("""
            **Concepts clés:**
            
            - **Stratégie dominante**: Meilleure réponse quelle que soit la stratégie des autres
            - **Équilibre de Nash**: Profil où aucun joueur ne peut améliorer son gain en changeant unilatéralement
            - **Optimum de Pareto**: Situation où on ne peut améliorer un joueur sans détériorer un autre
            - **Niveau de sécurité**: Gain maximum qu'un joueur peut garantir quel que soit le comportement des autres
            """)
    
except Exception as e:
    st.error(f"Une erreur est survenue: {str(e)}")
    st.error("Veuillez vérifier que tous les modules nécessaires sont correctement installés et que les chemins d'accès sont valides.")