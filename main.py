#!/usr/bin/env python3
"""
Script principal pour l'exécutable du dashboard simple ITA.
Ce fichier sera compilé en exe avec PyInstaller.
"""
import os
import sys
import webbrowser
import threading
import time

def open_browser():
    """Ouvre le navigateur après un court délai"""
    time.sleep(2)  # Attendre que Streamlit démarre
    try:
        webbrowser.open('http://localhost:8502')
        print("Navigateur ouvert sur http://localhost:8502")
    except Exception as e:
        print(f"Erreur lors de l'ouverture du navigateur: {e}")

if __name__ == "__main__":
    print("========================================")
    print("       Démarrage du dashboard ITA       ")
    print("========================================")
    
    # Récupérer le chemin du script
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, "dashboard_simple.py")
    
    print(f"Chargement du script: {script_path}")
    print("Le navigateur s'ouvrira automatiquement dans quelques secondes...")
    
    # Thread pour ouvrir le navigateur
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Modifier les arguments de sys.argv pour Streamlit
    sys.argv = ["streamlit", "run", script_path, "--server.port=8502", "--server.headless=true"]
    
    # Importer et lancer Streamlit directement (pas via subprocess)
    try:
        import streamlit.web.cli as stcli
        print("Lancement de Streamlit...")
        sys.exit(stcli.main())
    except Exception as e:
        print(f"\nERREUR: {e}")
        print("\nLe dashboard n'a pas pu être lancé.")
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
