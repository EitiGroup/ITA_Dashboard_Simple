@echo off
echo ============================================
echo    Création de l'exécutable ITA Dashboard
echo ============================================

REM Vérifier si le script d'installation a été exécuté
if not exist script_path.txt (
  echo ERREUR: Vous devez d'abord exécuter setup_env.bat
  echo pour installer Python et les dépendances.
  pause
  exit /b 1
)

REM Charger le chemin Python
set /p PYTHON_EXE=<script_path.txt
echo Utilisation de Python: %PYTHON_EXE%

REM Préparer les dossiers
if not exist docs mkdir docs
if not exist docs\images mkdir docs\images

REM Créer une image logo si nécessaire
if not exist docs\images\logo.png (
  echo Création d'une image logo temporaire...
  echo Logo Placeholder > docs\images\logo.png
)

REM Nettoyer les anciens fichiers de compilation
echo Nettoyage des fichiers existants...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
if exist "ITA Dashboard.spec" del "ITA Dashboard.spec"

REM Créer les dossiers nécessaires
mkdir build
mkdir dist

REM Création de l'exécutable
echo.
echo Création de l'exécutable...

"%PYTHON_EXE%" -m PyInstaller --clean ^^
  --noconfirm ^^
  --onefile ^^
  --name "ITA Dashboard" ^^
  --add-data "dashboard_simple.py;." ^^
  --add-data "pages;pages" ^^
  --add-data "docs;docs" ^^
  --hidden-import=streamlit.web.cli ^^
  --hidden-import=streamlit.runtime.scriptrunner.magic_funcs ^^
  --hidden-import=streamlit.runtime.scriptrunner ^^
  main.py

echo.
if %ERRORLEVEL% EQU 0 (
  echo Copie du fichier d'instructions pour l'utilisateur...
  copy CLIENT_README.txt dist\
  
  echo ============================================
  echo Compilation réussie!
  echo.
  echo L'exécutable se trouve dans le dossier "dist"
  echo Vous pouvez maintenant distribuer ces fichiers:
  echo - dist\ITA Dashboard.exe
  echo - dist\CLIENT_README.txt
  echo ============================================
) else (
  echo ERREUR: La compilation a échoué avec code %ERRORLEVEL%
  echo.
  echo Vérifiez que Streamlit fonctionne correctement avec:
  echo "%PYTHON_EXE%" -m streamlit run dashboard_simple.py
  echo ============================================
)

echo.
echo Pour déployer sur un serveur, consultez SERVER_DEPLOY.txt
echo.
pause
