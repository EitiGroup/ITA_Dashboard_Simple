@echo off
echo ===================================================
echo               DASHBOARD ITA
echo ===================================================
echo.

REM Vérifier si Python est disponible
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python detecte, lancement direct du dashboard...
    python -m streamlit run dashboard_simple.py --server.port=8502
) else (
    echo Python non detecte, recherche de Streamlit Portable...
    if exist "streamlit.exe" (
        echo Streamlit Portable trouve, lancement du dashboard...
        streamlit.exe run dashboard_simple.py --server.port=8502
    ) else (
        echo ERREUR: Ni Python ni Streamlit Portable n'ont ete trouves.
        echo.
        echo Veuillez consulter le fichier INSTALLATION_SANS_PYTHON.md
        echo pour des instructions d'installation alternatives.
    )
)

echo.
echo Si le dashboard ne s'est pas ouvert automatiquement,
echo ouvrez votre navigateur a l'adresse: http://localhost:8502
echo.
pause
