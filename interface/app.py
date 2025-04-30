import streamlit as st
import numpy as np
from modeles import Jeu, Joueur
from algorithmes import AnalyseurJeu # type: ignore
from utils import charger_jeu_classique, normaliser_gains

st.set_page_config(page_title="Analyse des Jeux Stratégiques", layout="wide")

# Configuration de la page
st.title("📊 Analyse des Jeux Stratégiques")
st.markdown("""
Cette application permet d'analyser les jeux stratégiques à 2 joueurs ou plus en utilisant différents concepts de théorie des jeux.
""")

# Sidebar pour la configuration
with st.sidebar:
    st.header("Configuration du Jeu")
    choix_jeu = st.selectbox(
        "Choisir un jeu",
        ["dilemme_prisonnier", "bataille_sexes", "personnalise"]
    )
    
    if choix_jeu == "personnalise":
        st.warning("La configuration personnalisée n'est pas encore implémentée")
    
    st.markdown("---")
    st.header("Options d'Analyse")
    analyse_nash = st.checkbox("Équilibre de Nash", True)
    analyse_pareto = st.checkbox("Optimum de Pareto", True)
    analyse_securite = st.checkbox("Niveaux de Sécurité", True)
    analyse_dominance = st.checkbox("Stratégies Dominantes", True)

# Chargement du jeu
try:
    if choix_jeu != "personnalise":
        jeu = charger_jeu_classique(choix_jeu)
        analyseur = AnalyseurJeu(jeu)
        
        # Affichage des matrices de gains
        st.subheader("Matrices de Gains")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Joueur 1**")
            st.dataframe(jeu.gains[1])
        
        with col2:
            st.markdown(f"**Joueur 2**")
            st.dataframe(jeu.gains[2])
        
        # Affichage des résultats
        st.subheader("Résultats de l'Analyse")
        
        if analyse_nash:
            with st.expander("Équilibre de Nash"):
                equilibres = analyseur.equilibre_nash()
                if equilibres:
                    st.write("Équilibres trouvés:")
                    for eq in equilibres:
                        noms = [jeu.get_strategie_name(i+1, s) for i, s in enumerate(eq)]
                        st.write(f"- Profil {eq}: {', '.join(noms)}")
                else:
                    st.warning("Aucun équilibre de Nash en stratégies pures trouvé")
        
        if analyse_pareto:
            with st.expander("Optimum de Pareto"):
                pareto_optima = analyseur.optimum_pareto()
                if pareto_optima:
                    st.write("Optima de Pareto trouvés:")
                    for opt in pareto_optima:
                        noms = [jeu.get_strategie_name(i+1, s) for i, s in enumerate(opt)]
                        st.write(f"- Profil {opt}: {', '.join(noms)}")
                else:
                    st.warning("Aucun optimum de Pareto trouvé")
        
        if analyse_securite:
            with st.expander("Niveaux de Sécurité"):
                for j in jeu.joueurs:
                    valeur, strat = analyseur.niveau_securite(j.id)
                    st.write(f"**Joueur {j.id}**:")
                    st.write(f"- Stratégie de sécurité: {jeu.get_strategie_name(j.id, strat)}")
                    st.write(f"- Gain garanti: {valeur:.2f}")
                    st.write("---")
        
        if analyse_dominance:
            with st.expander("Stratégies Dominantes"):
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