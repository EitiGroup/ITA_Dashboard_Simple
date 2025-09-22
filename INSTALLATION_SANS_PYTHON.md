# Comment utiliser le Dashboard sans installer Python

Si vous rencontrez des difficultés avec l'installation de Python et des dépendances, vous pouvez utiliser Streamlit Portable, qui ne nécessite pas d'installation.

## Option 1: Streamlit Portable

1. **Téléchargez Streamlit Portable** depuis ce lien :
   https://github.com/whitphx/streamlit-portable/releases

2. **Extrayez le fichier ZIP** dans un dossier (par exemple `C:\streamlit-portable`)

3. **Copiez les fichiers du dashboard** dans un sous-dossier :
   - Créez un dossier `C:\streamlit-portable\dashboard`
   - Copiez `dashboard_simple.py` et le dossier `pages` dans ce dossier

4. **Créez un fichier batch pour lancer le dashboard** :
   - Créez un fichier `lancer_dashboard.bat` dans le dossier principal avec ce contenu :
   ```batch
   @echo off
   cd /d %~dp0
   streamlit.exe run dashboard\dashboard_simple.py --server.port=8502
   pause
   ```

5. **Double-cliquez sur `lancer_dashboard.bat`** pour démarrer le dashboard

## Option 2: Installation Python simplifiée

Si vous préférez installer Python correctement :

1. **Téléchargez Python 3.9** depuis le site officiel :
   https://www.python.org/downloads/release/python-3913/

2. **Lors de l'installation** :
   - Cochez IMPÉRATIVEMENT "Add Python to PATH"
   - Utilisez l'option "Customize installation"
   - Assurez-vous que toutes les cases sont cochées
   - Choisissez un chemin d'installation simple comme `C:\Python39`

3. **Redémarrez votre ordinateur**

4. **Ouvrez PowerShell en tant qu'administrateur** et exécutez :
   ```powershell
   python -m pip install streamlit pandas numpy pymssql altair
   cd chemin\vers\votre\dossier
   python -m streamlit run dashboard_simple.py
   ```

## Option 3: Version en ligne du dashboard

Si vous disposez d'un serveur web, nous pouvons configurer une version hébergée du dashboard accessible depuis n'importe quel navigateur sans installation.
