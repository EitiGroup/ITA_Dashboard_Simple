#!/usr/bin/env python3
"""
Script de test pour vérifier si Streamlit est correctement installé
"""
import sys

print("Python version:", sys.version)
print("Python executable:", sys.executable)

try:
    import streamlit
    print("Streamlit version:", streamlit.__version__)
    print("Streamlit path:", streamlit.__path__)
    print("Streamlit bootstrap disponible:", hasattr(streamlit, 'web') and hasattr(streamlit.web, 'bootstrap'))
    print("Test réussi! Streamlit est correctement installé.")
except ImportError as e:
    print("ERREUR: Impossible d'importer streamlit:", e)
    print("\nEssayez d'installer Streamlit avec la commande:")
    print("pip install streamlit==1.28.0")

input("\nAppuyez sur Entrée pour quitter...")
