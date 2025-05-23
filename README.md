﻿# 🎮 Strategic Game Analysis App

An interactive Streamlit web application to analyze strategic games using concepts from game theory, including:
- Nash Equilibrium
- Pareto Optimality
- Dominant Strategies
- Security Levels
- Iterated Elimination of Strictly Dominated Strategies (IESDS)

## 🧠 Features

- Support for **2 to 5 players**
- Custom game creation with **named strategies** and **custom payoff matrices**
- Preloaded classic games: Prisoner's Dilemma, Battle of the Sexes
- Multiple analysis tools:
  - Nash Equilibrium in pure strategies
  - Pareto optimum profiles
  - Dominant strategies (strict & weak)
  - Security level strategies
  - IESDS with **elimination path displayed**

## 📌 Technologies Used

- [Python 3.9+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- NumPy, Pandas

## 📂 Project Structure
├── core/
│   ├── modeles.py        # Classes Joueur, Jeu
│   ├── algorithmes.py    # Implémentation des concepts (Nash, Pareto, IESDS, etc.)
│   └── utils.py          # Fonctions auxiliaires (Exemples réseaux, Jeux théoriques)
└── interface/            # Interface utilisateur
    └── app.py            # Main Streamlit app


## 🚀 Getting Started

### Prerequisites

- Python 3.9 or newer
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/strategic-game-analyzer.git
cd strategic-game-analyzer

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```
### Running the App
```bash
streamlit run app.py
