# Guide de déploiement du Dashboard ITA sur le serveur d'usine

## Configuration du serveur

D'après votre description, vous êtes connecté sur un serveur Windows Server (identifiable par le coquillage jaune PowerShell sur fond bleu). Ce serveur possède :
- Un disque C: local 
- Un disque Z: partagé
- Une session TSE1

Ce type de serveur est parfait pour héberger votre dashboard en continu (24h/24) et le rendre accessible à tous les utilisateurs sur le réseau d'entreprise.

## Étape 1 : Où installer le dashboard ?

**Option recommandée : Lecteur Z: partagé**

```
Z:\Applications\ITA_Dashboard
```

Avantages :
- Accessible à tous les utilisateurs autorisés
- Facilite les sauvegardes par le service IT
- Stockage généralement plus important

## Étape 2 : Fichiers à installer

1. Créez le dossier d'installation
   ```
   mkdir Z:\Applications\ITA_Dashboard
   ```

2. Copiez ces fichiers dans le dossier :
   - `ITA Dashboard.exe` (l'exécutable principal)
   - `CLIENT_README.txt` (instructions)
   - `service_setup.bat` (script d'installation du service)

## Étape 3 : Installation en tant que service Windows

Pour que le dashboard fonctionne 24h/24 sans interruption (même sans session utilisateur active), vous devez l'installer en tant que service Windows :

1. Ouvrez PowerShell en mode Administrateur
2. Naviguez jusqu'au dossier d'installation :
   ```powershell
   cd Z:\Applications\ITA_Dashboard
   ```
3. Exécutez le script d'installation du service :
   ```powershell
   .\service_setup.bat
   ```

Ce script va :
- Télécharger et configurer NSSM (outil de gestion de services)
- Installer le dashboard comme service Windows
- Configurer le démarrage automatique
- Créer des fichiers de logs

## Étape 4 : Vérification de la connexion à la base de données

> **IMPORTANT** : Le dashboard ne doit afficher QUE des données réelles provenant de la base de données SQL Server (192.168.1.250). En cas de problème de connexion, le dashboard affichera des valeurs vides ou nulles, mais jamais de données fictives.

Vérifiez que le serveur peut accéder à la base de données :

```powershell
Test-NetConnection -ComputerName 192.168.1.250 -Port 1433
```

Si la connexion échoue, contactez votre administrateur réseau.

## Étape 5 : Accès au dashboard

Une fois le service démarré, le dashboard sera accessible depuis n'importe quel poste du réseau d'entreprise via :

```
http://[NOM_DU_SERVEUR]:8502
```

Remplacez `[NOM_DU_SERVEUR]` par le nom réel de votre serveur (probablement le nom associé à la session TSE1).

Par exemple : `http://SERV-TSE1:8502`

## Vérifications et maintenance

### Pour vérifier que le service fonctionne :

1. Sur le serveur, ouvrez la console des services :
   ```
   services.msc
   ```
2. Recherchez le service "ITA Dashboard" et vérifiez qu'il est en cours d'exécution

### Consulter les logs :

Les logs se trouvent dans le dossier :
```
Z:\Applications\ITA_Dashboard\logs
```

### Redémarrer le service :

En cas de problème, vous pouvez redémarrer le service :
```powershell
Restart-Service -Name "ITA Dashboard"
```

## Notes spécifiques sur la base de données

> **Rappel important** : Dans la base PMI (SQL Server 192.168.1.250), les codes société (champ PFCTETS) sont vides, ce qui rend impossible le filtrage par entité (ITA Moulding Process vs ITA Solutions). Cette particularité est déjà prise en compte dans les requêtes SQL utilisées par le dashboard.

## Support

En cas de problème avec le dashboard, consultez d'abord les fichiers de logs. Si le problème persiste, contactez le développeur du dashboard.
