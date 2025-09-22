@echo off
echo =====================================================
echo     Installation du service ITA Dashboard
echo =====================================================

REM Vérifier les droits d'administrateur
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERREUR: Vous devez exécuter ce script en tant qu'administrateur!
    echo Clic droit sur le fichier et sélectionnez "Exécuter en tant qu'administrateur"
    pause
    exit /b 1
)

REM Déterminer le chemin d'installation
set INSTALL_PATH=%~dp0
echo Chemin d'installation: %INSTALL_PATH%

REM Télécharger et installer NSSM (outil de gestion de services Windows)
if not exist "%INSTALL_PATH%\nssm\nssm.exe" (
    echo Téléchargement de NSSM (gestionnaire de services)...
    powershell -Command "Invoke-WebRequest -Uri https://nssm.cc/release/nssm-2.24.zip -OutFile %INSTALL_PATH%\nssm.zip"
    powershell -Command "Expand-Archive -Path %INSTALL_PATH%\nssm.zip -DestinationPath %INSTALL_PATH%\nssm_temp"
    mkdir "%INSTALL_PATH%\nssm"
    copy "%INSTALL_PATH%\nssm_temp\nssm-2.24\win64\nssm.exe" "%INSTALL_PATH%\nssm\"
    rmdir /s /q "%INSTALL_PATH%\nssm_temp"
    del "%INSTALL_PATH%\nssm.zip"
)

echo Configuration du service Windows...

REM Arrêter et supprimer le service s'il existe déjà
"%INSTALL_PATH%\nssm\nssm.exe" stop "ITA Dashboard" confirm >nul 2>&1
"%INSTALL_PATH%\nssm\nssm.exe" remove "ITA Dashboard" confirm >nul 2>&1

REM Installer le service avec NSSM
"%INSTALL_PATH%\nssm\nssm.exe" install "ITA Dashboard" "%INSTALL_PATH%\ITA Dashboard.exe"
"%INSTALL_PATH%\nssm\nssm.exe" set "ITA Dashboard" DisplayName "ITA Dashboard"
"%INSTALL_PATH%\nssm\nssm.exe" set "ITA Dashboard" Description "Dashboard d'analyse de données ITA"
"%INSTALL_PATH%\nssm\nssm.exe" set "ITA Dashboard" AppDirectory "%INSTALL_PATH%"
"%INSTALL_PATH%\nssm\nssm.exe" set "ITA Dashboard" AppStdout "%INSTALL_PATH%\logs\service_output.log"
"%INSTALL_PATH%\nssm\nssm.exe" set "ITA Dashboard" AppStderr "%INSTALL_PATH%\logs\service_error.log"
"%INSTALL_PATH%\nssm\nssm.exe" set "ITA Dashboard" AppRotateFiles 1
"%INSTALL_PATH%\nssm\nssm.exe" set "ITA Dashboard" Start SERVICE_AUTO_START

REM Créer le dossier de logs
if not exist "%INSTALL_PATH%\logs" mkdir "%INSTALL_PATH%\logs"

REM Démarrer le service
echo Démarrage du service...
net start "ITA Dashboard"

echo =====================================================
echo     Installation du service terminée!
echo =====================================================
echo.
echo Le dashboard ITA est maintenant configuré pour démarrer
echo automatiquement avec Windows et fonctionner 24h/24.
echo.
echo Pour y accéder, utilisez l'adresse:
echo http://NOM_DU_SERVEUR:8502
echo.
echo (Remplacez NOM_DU_SERVEUR par le nom réel de votre serveur)
echo.
echo Logs du service disponibles dans: %INSTALL_PATH%\logs
echo =====================================================
echo.
pause
