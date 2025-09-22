@echo off
echo =====================================================
echo Configuration de l'environnement pour ITA Dashboard
echo =====================================================

REM Rechercher l'installation de Python
echo Recherche de Python...

REM Chemins possibles pour Python
set PYTHON_PATHS=^^
%LOCALAPPDATA%\Programs\Python\Python39\python.exe;^^
%LOCALAPPDATA%\Programs\Python\Python310\python.exe;^^
%LOCALAPPDATA%\Programs\Python\Python311\python.exe;^^
%LOCALAPPDATA%\Programs\Python\Python312\python.exe;^^
%LOCALAPPDATA%\Programs\Python\Python313\python.exe;^^
C:\Python39\python.exe;^^
C:\Python310\python.exe;^^
C:\Python311\python.exe;^^
C:\Python312\python.exe;^^
C:\Python313\python.exe

set PYTHON_EXE=

for %%p in (%PYTHON_PATHS%) do (
    if exist %%p (
        set PYTHON_EXE=%%p
        echo Python trouvé : %%p
        goto python_found
    )
)

:no_python
echo Python n'a pas été trouvé dans les chemins standard.
echo.
echo Veuillez télécharger et installer Python depuis :
echo https://www.python.org/downloads/
echo.
echo IMPORTANT : Cochez "Add Python to PATH" lors de l'installation.
echo.
pause
exit /b 1

:python_found
echo.
echo Installation des dépendances...

"%PYTHON_EXE%" -m pip install --upgrade pip
"%PYTHON_EXE%" -m pip install streamlit==1.28.0
"%PYTHON_EXE%" -m pip install pandas==2.0.0
"%PYTHON_EXE%" -m pip install numpy==1.24.3
"%PYTHON_EXE%" -m pip install pymssql==2.2.7
"%PYTHON_EXE%" -m pip install altair==5.0.1
"%PYTHON_EXE%" -m pip install pyinstaller==6.0.0

echo.
echo Création de script_path.txt avec le chemin Python...
echo %PYTHON_EXE% > script_path.txt

echo.
echo =====================================================
echo Installation terminée!
echo.
echo Pour créer l'exécutable, exécutez maintenant:
echo build.bat
echo =====================================================
pause
