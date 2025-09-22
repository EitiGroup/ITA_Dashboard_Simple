@echo off
echo =====================================================
echo Configuration de l'environnement pour ITA Dashboard
echo =====================================================

REM Rechercher Python dans le PATH
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python trouve dans le PATH
    set PYTHON_EXE=python
    goto python_found
)

REM Vérifier les chemins d'installation standard
if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
    echo Python 3.9 trouve
    set PYTHON_EXE="%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    goto python_found
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    echo Python 3.10 trouve
    set PYTHON_EXE="%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto python_found
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    echo Python 3.11 trouve
    set PYTHON_EXE="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto python_found
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    echo Python 3.12 trouve
    set PYTHON_EXE="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto python_found
)

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    echo Python 3.13 trouve
    set PYTHON_EXE="%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto python_found
)

echo Python n'a pas ete trouve. Veuillez installer Python depuis:
echo https://www.python.org/downloads/
echo IMPORTANT: Cochez "Add Python to PATH" lors de l'installation.
pause
exit /b 1

:python_found
echo Installation des dependances...
%PYTHON_EXE% -m pip install --upgrade pip
%PYTHON_EXE% -m pip install streamlit==1.28.0
%PYTHON_EXE% -m pip install pandas==2.0.0
%PYTHON_EXE% -m pip install numpy==1.24.3
%PYTHON_EXE% -m pip install pymssql==2.2.7
%PYTHON_EXE% -m pip install altair==5.0.1
%PYTHON_EXE% -m pip install pyinstaller==6.0.0

echo %PYTHON_EXE% > script_path.txt

echo =====================================================
echo Installation terminee!
echo.
echo Pour creer l'executable, executez maintenant:
echo build.bat
echo =====================================================
pause
