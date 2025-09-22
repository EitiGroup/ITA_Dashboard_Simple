import streamlit as st
import pandas as pd
import pymssql
import numpy as np
import random
import os
from datetime import datetime, timedelta
import time

# Cache désactivé pour éviter les problèmes
# st.cache_data.clear()

DB_SERVER = "192.168.1.250"
DB_USER = "sa"
DB_PASSWORD = "cegid.2016"
DB_NAME = "PMI"

def get_connection():
    """Établit une connexion à la base de données SQL Server PMI
    Les tests ont montré que la base PMI existe sur le serveur et contient les données.
    """
    try:
        # Se connecter directement à la base PMI
        conn = pymssql.connect(
            server='192.168.1.250',
            user='sa',
            password='cegid.2016',
            database='PMI',  # Utiliser PMI qui contient les données
            timeout=30,
            login_timeout=30
        )
        
        return conn
    except pymssql.Error as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        st.warning("⚠️ Il semble y avoir un problème de connexion à la base de données. Vérifiez que:\n"
                  "1. Le serveur SQL est démarré\n"
                  "2. Le réseau est accessible\n"
                  "3. Le VPN est actif\n"
                  "4. Les identifiants sont corrects")
        # Retourner None pour que les fonctions puissent gérer l'absence de connexion
        return None

# Cache désactivé temporairement
def execute_query(query):
    conn = None
    try:
        conn = get_connection()
        if conn:
            df = pd.read_sql(query, conn)
            return df
        else:

            pass

        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

# Cache désactivé temporairement
def get_sales_data(entity_filter="Groupe ITA"):
    """
    Récupère les données de ventes à partir des vues OData
    
    Cette fonction:
    1. Utilise la vue OData.LineCustomerInvoiceList qui contient les données de factures
    2. Filtre par LineDocumentCompany pour sélectionner l'entité correcte
    3. Filtre les codes comptables commençant par '70'
    4. Retourne un DataFrame pandas avec les données formatées
    
    Utilisé dans: dashboard.py -> fonction plot_rolling_12_month_comparison
    Affiché dans: Tableau "Évolution du CA sur 12 mois"
    """
    conn = get_connection()
    if not conn:
        st.error(f"Impossible de se connecter à la base de données. Aucune donnée ne sera affichée.")
        # Retourner un DataFrame vide avec la structure attendue
        return pd.DataFrame(columns=[
            "LineDocumentDocumentDate", "LineDocumentAmount", "LineDocumentCode",
            "LineDocumentItemDescriptionOne", "LineDocumentQuantity",
            "LineDocumentThirdPartyAccount", "InvoiceNumber",
            "year", "month", "day"
        ])
        
    try:
        # Vérifier qu'on est bien connecté à PMI
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME()")
        current_db = cursor.fetchone()[0]
        
        if current_db != 'PMI':
            st.warning(f"Connecté à la base {current_db} au lieu de PMI. Tentative de changement de base...")
            try:
                cursor.execute("USE PMI")
                
            except pymssql.Error as e:
                st.error(f"Erreur lors du changement vers la base PMI: {e}")
                return pd.DataFrame(columns=[
                    "LineDocumentDocumentDate", "LineDocumentAmount", "LineDocumentCode",
                    "LineDocumentItemDescriptionOne", "LineDocumentQuantity",
                    "LineDocumentThirdPartyAccount", "InvoiceNumber",
                    "year", "month", "day"
                ])
        
        # Utiliser directement la table PFACCLI qui est disponible d'après nos tests
        try:
            # Vérifier que PFACCLI existe
            cursor.execute("SELECT OBJECT_ID('dbo.PFACCLI')")
            table_id = cursor.fetchone()[0]
            
            if not table_id:
                st.warning("La table PFACCLI n'existe pas. Impossible de récupérer les données.")
                return pd.DataFrame(columns=[
                    "LineDocumentDocumentDate", "LineDocumentAmount", "LineDocumentCode",
                    "LineDocumentItemDescriptionOne", "LineDocumentQuantity",
                    "LineDocumentThirdPartyAccount", "InvoiceNumber",
                    "year", "month", "day"
                ])
            
            # Déterminer les colonnes disponibles (utiliser les noms corrects)
            
            
            
        except Exception as e:
            st.error(f"Erreur lors de la vérification de la table: {e}")
            return pd.DataFrame()

        # Construction de la requête avec méthode MIN
        query = """
        WITH CommandeSociete AS (
            SELECT LCKTNUMERO, MIN(LCKTSOC) as LCKTSOC
            FROM dbo.LCOMCLI GROUP BY LCKTNUMERO
        ),
        FacturesUniques AS (
            SELECT
                CAST(p.PFCJDATE AS DATETIME) as LineDocumentDocumentDate,
                MIN(p.PFCNMT) as LineDocumentAmount, 
                p.PFKTFACTUR as LineDocumentCode,
                p.PFCTLIB as LineDocumentItemDescriptionOne, 
                1 as LineDocumentQuantity, 
                p.PFCTCTIERS as LineDocumentThirdPartyAccount,
                p.PFKTFACTUR as InvoiceNumber,
                YEAR(CAST(p.PFCJDATE AS DATETIME)) as year,
                MONTH(CAST(p.PFCJDATE AS DATETIME)) as month,
                DAY(CAST(p.PFCJDATE AS DATETIME)) as day,
                COALESCE(cs.LCKTSOC, 'Non défini') as CodeSociete
            FROM dbo.PFACCLI p
            LEFT JOIN CommandeSociete cs ON p.PFCTCDE = cs.LCKTNUMERO
            WHERE p.PFCJDATE IS NOT NULL
              AND (p.PFITCPT LIKE '70%' OR (p.PFITCPT LIKE '79%' AND p.PFITCPT != '7910000000' AND p.PFITCPT != '7083000000'))
              AND p.PFCTSENS = 'C'  -- Uniquement lignes de crédit
        """
        
        # Nouvelles correspondances
        if entity_filter == "ITA Moulding Process":
            query += " AND COALESCE(cs.LCKTSOC, 'Non défini') = '100'"
        elif entity_filter == "ITA Solutions":
            query += " AND COALESCE(cs.LCKTSOC, 'Non défini') = '400'"
        elif entity_filter == "Vindy":
            query += " AND COALESCE(cs.LCKTSOC, 'Non défini') = '300'"
        elif entity_filter == "Groupe ITA":
            query += " AND COALESCE(cs.LCKTSOC, 'Non défini') IN ('100', '400')"
            
        query += """
            GROUP BY 
                p.PFKTFACTUR, p.PFITCPT, CAST(p.PFCJDATE AS DATETIME),
                p.PFCTLIB, p.PFCTCTIERS, COALESCE(cs.LCKTSOC, 'Non défini')
        )
        SELECT * FROM FacturesUniques
        ORDER BY LineDocumentDocumentDate
        """
            
        df = pd.read_sql(query, conn)
        
        if df.empty:
            st.warning(f"Aucune donnée trouvée pour l'entité: {entity_filter}.")
            return df
        
        df["LineDocumentDocumentDate"] = pd.to_datetime(df["LineDocumentDocumentDate"])
        
        # S'assurer que les années, mois et jours sont correctement typés
        df["year"] = df["year"].astype(int)
        df["month"] = df["month"].astype(int)
        df["day"] = df["day"].astype(int)
        
        
        return df
    except pymssql.Error as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        # Retourner un DataFrame vide avec la structure attendue
        return pd.DataFrame(columns=[
            "LineDocumentDocumentDate", "LineDocumentAmount", "LineDocumentCompany", 
            "LineDocumentCode", "LineDocumentItemDescriptionOne", "LineDocumentQuantity",
            "LineDocumentThirdPartyAccount", "InvoiceNumber", "year", "month", "day"
        ])
    finally:
        if conn:
            conn.close()

# La fonction create_demo_sales_data a été supprimée car elle générait des données fictives

# Cache désactivé temporairement
def get_orders_data(entity_filter="Groupe ITA"):
    """
    Récupère les données de commandes à partir de la vue OData.LineCustomerOrderList
    
    Cette fonction:
    1. Utilise la vue OData pour accéder aux données de commandes clients
    2. Filtre par LineDocumentCompany pour sélectionner l'entité correcte
    3. Filtre les codes comptables commençant par '70'
    4. Retourne un DataFrame pandas avec les données formatées
    """
    conn = None
    try:
        conn = get_connection()
        if not conn:
            st.error(f"Impossible de se connecter à la base de données. Aucune donnée de commande ne sera affichée.")
            # Retourner un DataFrame vide avec la structure attendue
            return pd.DataFrame(columns=[
                "LineDocumentDocumentDate", "LineDocumentAmount", "LineDocumentCompany", 
                "LineDocumentCode", "LineDocumentItemDescriptionOne", "LineDocumentQuantity",
                "LineDocumentThirdPartyAccount", "LineDocumentDeliveryDateOfLast"
            ])
            
        # Utiliser la vue OData.LineCustomerOrderList avec requête simplifiée
        query = """
        SELECT 
            LineDocumentDocumentDate,
            LineDocumentAmount,
            LineDocumentCode,
            LineDocumentItemDescriptionOne,
            LineDocumentQuantity,
            LineDocumentThirdPartyAccount,
            LineDocumentDeliveryDateOfLast
        FROM [OData].[LineCustomerOrderList]
        """
        
        # Désactivé temporairement car LineDocumentCompany n'existe pas
        # if entity_filter == "ITA Moulding Process":
        #     query += " AND LineDocumentCompany = '100'"
        # elif entity_filter == "ITA Solutions":
        #     query += " AND LineDocumentCompany IN ('200', '400')"
        # elif entity_filter == "ITA Holding":
        #     query += " AND LineDocumentCompany = '300'"
        
        query += " ORDER BY LineDocumentDocumentDate DESC"
            
        df = pd.read_sql(query, conn)
        
        if df.empty:
            st.warning(f"Aucune donnée de commande trouvée pour l'entité: {entity_filter}.")
            return df
            
        
        return df
        
    except pymssql.Error as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        return pd.DataFrame(columns=[
            "LineDocumentDocumentDate", "LineDocumentAmount", "LineDocumentCompany", 
            "LineDocumentCode", "LineDocumentItemDescriptionOne", "LineDocumentQuantity",
            "LineDocumentThirdPartyAccount", "LineDocumentDeliveryDateOfLast"
        ])
    finally:
        if conn:
            conn.close()
            
# La fonction create_demo_orders_data a été supprimée car elle générait des données fictives

# Cache désactivé temporairement
def get_offers_data(entity_filter="Groupe ITA"):
    """
    Récupère les données d'offres à partir de la vue OData.LineCustomerOfferList
    
    Cette fonction:
    1. Utilise la vue OData pour accéder aux données d'offres clients
    2. Filtre par LineDocumentCompany pour sélectionner l'entité correcte
    3. Filtre les codes comptables commençant par '70'
    4. Retourne un DataFrame pandas avec les données formatées
    """
    conn = None
    try:
        conn = get_connection()
        if not conn:
            st.error(f"Impossible de se connecter à la base de données. Aucune donnée d'offre ne sera affichée.")
            # Retourner un DataFrame vide avec la structure attendue
            return pd.DataFrame(columns=[
                "LineDocumentDocumentDate", "LineDocumentAmount", "LineDocumentCompany", 
                "LineDocumentCode", "LineDocumentItemDescriptionOne", "LineDocumentQuantity",
                "LineDocumentThirdPartyAccount"
            ])
            
        # Utiliser la vue OData.LineCustomerOfferList avec requête simplifiée
        query = """
        SELECT 
            LineDocumentDocumentDate,
            LineDocumentAmount,
            LineDocumentCode,
            LineDocumentItemDescriptionOne,
            LineDocumentQuantity,
            LineDocumentThirdPartyAccount
        FROM [OData].[LineCustomerOfferList]
        """
        
        # Désactivé temporairement car LineDocumentCompany n'existe pas
        # if entity_filter == "ITA Moulding Process":
        #     query += " AND LineDocumentCompany = '100'"
        # elif entity_filter == "ITA Solutions":
        #     query += " AND LineDocumentCompany IN ('200', '400')"
        # elif entity_filter == "ITA Holding":
        #     query += " AND LineDocumentCompany = '300'"
        
        query += " ORDER BY LineDocumentDocumentDate DESC"
            
        df = pd.read_sql(query, conn)
        
        if df.empty:
            st.warning(f"Aucune donnée d'offre trouvée pour l'entité: {entity_filter}.")
            return df
            
        
        return df
        
    except pymssql.Error as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        # Retourner un DataFrame vide avec la structure attendue
        return pd.DataFrame(columns=[
            "LineDocumentDocumentDate", "LineDocumentAmount", "LineDocumentCompany", 
            "LineDocumentCode", "LineDocumentItemDescriptionOne", "LineDocumentQuantity",
            "LineDocumentThirdPartyAccount"
        ])
    finally:
        if conn:
            conn.close()
            
# La fonction create_demo_offers_data a été supprimée car elle générait des données fictives

# Cache désactivé temporairement
def get_delivery_data(entity_filter="Groupe ITA"):
    # Les tables LBLIVCLI et EBLIVCLI n'existent pas dans la base de données actuelle
    # Après recherche approfondie, aucune table de livraisons n'a été identifiée
    
    # Tentative de connexion uniquement pour tracer l'état de la connexion
    conn = None
    try:
        conn = get_connection()
        if not conn:
            st.warning("Pas de connexion à la base de données, aucune donnée de livraison ne sera affichée.")
    finally:
        if conn:
            conn.close()
    
    # Retourne un DataFrame vide avec la structure attendue
    
    return pd.DataFrame(columns=[
        "LineDocumentDocumentDate", "LineDocumentAmount", "LineDocumentCompany", 
        "LineDocumentCode", "LineDocumentItemDescriptionOne", "LineDocumentQuantity",
        "LineDocumentThirdPartyAccount"
    ])
            
# La fonction create_demo_delivery_data a été supprimée car elle générait des données fictives

# Cache désactivé temporairement
def get_credit_notes_data(entity_filter="Groupe ITA"):
    try:
        # Vérifier s'il existe une table d'avoirs dans la base de données
        conn = None
        try:
            conn = get_connection()
            if not conn:
                st.warning("Pas de connexion à la base de données, aucune donnée d'avoir ne sera affichée.")
                return pd.DataFrame(columns=[
                    "LineDocumentDocumentDate", "LineDocumentAmount", "LineDocumentCompany", 
                    "LineDocumentCode", "LineDocumentItemDescriptionOne", "LineDocumentQuantity",
                    "LineDocumentThirdPartyAccount"
                ])
                
            # Vérifier la présence de tables d'avoirs dans la base
            query_check = """
            SELECT TOP 1 1 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME IN ('AVOIR', 'CREDITMEMO', 'PFAVOIR', 'PINAVOIR')
            """
            
            df_check = pd.read_sql(query_check, conn)
            
            if not df_check.empty:
                # Table trouvée, faire la requête appropriée
                st.warning("Tables d'avoirs identifiées mais structure non définie. Requête à implémenter.")
            else:

                pass

            return pd.DataFrame(columns=[
                    "LineDocumentDocumentDate", "LineDocumentAmount", "LineDocumentCompany",
                    "LineDocumentCode", "LineDocumentItemDescriptionOne", "LineDocumentQuantity",
                    "LineDocumentThirdPartyAccount"
                ])

        finally:
            if conn:
                conn.close()
                
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données d'avoirs : {e}")
        return pd.DataFrame(columns=[
            "LineDocumentDocumentDate", "LineDocumentAmount", "LineDocumentCompany", 
            "LineDocumentCode", "LineDocumentItemDescriptionOne", "LineDocumentQuantity",
            "LineDocumentThirdPartyAccount"
        ])

# Cache désactivé temporairement
def get_quality_nonconformity_data(entity_filter="Groupe ITA"):
    """Récupère des données de non-conformité depuis la table NONCONFO si disponible"""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            st.error("Pas de connexion à la base de données, aucune donnée de non-conformité ne sera affichée.")
            # Retourner un DataFrame vide avec la structure attendue
            return pd.DataFrame(columns=[
                "DateCreation", "CodeSociete", "NumeroNC", "CodeClient", "TypeNC", "PrioriteNC",
                "CodeArticle", "DescriptionArticle", "Quantite", "OrigineNC", "Description", "StatutSuivi"
            ])
        
        # Essayer d'accéder à la table NONCONFO
        query = """
        SELECT 
            CAST(NC.DATECRE AS DATETIME) AS DateCreation,
            NC.SOCIETE AS CodeSociete,
            NC.NUMERO AS NumeroNC, 
            NC.CLIENT AS CodeClient,
            NC.TYPENC AS TypeNC,
            NC.PRIORITE AS PrioriteNC,
            NC.ARTICCOD AS CodeArticle,
            NC.ARTICLIB AS DescriptionArticle,
            NC.QUANTI AS Quantite,
            NC.ORIGIDISC AS OrigineNC,
            NC.DESCNC AS Description,
            NC.SUIVI AS StatutSuivi
        FROM dbo.NONCONFO NC
        WHERE 1=1
        """
        
        # Les codes société sont vides dans la base, on ne filtre pas
        # if entity_filter == "ITA Moulding Process":
        #     query += " AND NC.SOCIETE = '100'"
        # elif entity_filter == "ITA Solutions":
        #     query += " AND NC.SOCIETE IN ('200', '300', '400')"
            
        query += " ORDER BY NC.DATECRE DESC"
        
        try:
            df = pd.read_sql(query, conn)
            if df.empty:
                return df
            else:

                pass

            return pd.DataFrame()

        except Exception as e:
            st.warning(f"La table NONCONFO n'est pas accessible: {e}")
            # Retourner un DataFrame vide avec la structure attendue
            return pd.DataFrame(columns=[
                "DateCreation", "CodeSociete", "NumeroNC", "CodeClient", "TypeNC", "PrioriteNC",
                "CodeArticle", "DescriptionArticle", "Quantite", "OrigineNC", "Description", "StatutSuivi"
            ])
        
    except pymssql.Error as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        # Retourner un DataFrame vide avec la structure attendue
        return pd.DataFrame(columns=[
            "DateCreation", "CodeSociete", "NumeroNC", "CodeClient", "TypeNC", "PrioriteNC",
            "CodeArticle", "DescriptionArticle", "Quantite", "OrigineNC", "Description", "StatutSuivi"
        ])
    finally:
        if conn:
            conn.close()

# La fonction create_demo_quality_data a été supprimée car elle générait des données fictives

# Cache désactivé temporairement
def get_maintenance_data(entity_filter="Groupe ITA"):
    """Récupère des données de maintenance des équipements si disponibles"""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            st.error("Pas de connexion à la base de données, aucune donnée de maintenance ne sera affichée.")
            # Retourner un DataFrame vide avec la structure attendue
            return pd.DataFrame(columns=[
                "DateIntervention", "CodeSociete", "Equipement", "TypeIntervention", "DureeHeures",
                "Technicien", "Description", "StatutIntervention", "CoutPieces", "TempsDArret"
            ])
        
        # Tentative d'accès aux tables de maintenance
        try:
            # Vérifier si la table de maintenance existe
            query_check = """
            SELECT TOP 1 1 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'HISBAC'
            """
            df_check = pd.read_sql(query_check, conn)
            
            if not df_check.empty:
                # Table existe, faire une requête (format à adapter selon la vraie structure)
                query = """
                SELECT 
                    -- Compléter avec la vraie structure de la table HISBAC
                    -- Exemple:
                    -- CAST(date_colonne AS DATETIME) AS DateIntervention,
                    -- societe_colonne AS CodeSociete,
                    -- etc.
                FROM dbo.HISBAC
                WHERE 1=1
                """
                
                # Les codes société sont vides dans la base, on ne filtre pas
                # if entity_filter == "ITA Moulding Process":
                #     query += " AND societe_colonne = '100'"
                # elif entity_filter == "ITA Solutions":
                #     query += " AND societe_colonne IN ('200', '300', '400')"
                    
                query += " ORDER BY date_colonne DESC"
                
                # Décommenter quand la structure est connue
                # df = pd.read_sql(query, conn)
                # return df
            
            
            return pd.DataFrame(columns=[
                "DateIntervention", "CodeSociete", "Equipement", "TypeIntervention", "DureeHeures",
                "Technicien", "Description", "StatutIntervention", "CoutPieces", "TempsDArret"
            ])
        except Exception as e:
            st.warning(f"Impossible d'accéder aux tables de maintenance: {e}")
            return pd.DataFrame(columns=[
                "DateIntervention", "CodeSociete", "Equipement", "TypeIntervention", "DureeHeures",
                "Technicien", "Description", "StatutIntervention", "CoutPieces", "TempsDArret"
            ])
    except pymssql.Error as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        return pd.DataFrame(columns=[
            "DateIntervention", "CodeSociete", "Equipement", "TypeIntervention", "DureeHeures",
            "Technicien", "Description", "StatutIntervention", "CoutPieces", "TempsDArret"
        ])
    finally:
        if conn:
            conn.close()

# La fonction create_demo_maintenance_data a été supprimée car elle générait des données fictives

# Cache désactivé temporairement
def get_top_clients(entity_filter="Groupe ITA", limit=10, year=None):
    """
    Récupère les top clients par chiffre d'affaires pour une entité et une année données
    en utilisant les vues OData
    """
    if year is None:
        year = datetime.now().year
    
    conn = None
    try:
        conn = get_connection()
        if not conn:
            st.error("Impossible de se connecter à la base de données.")
            return pd.DataFrame(columns=["CodeClient", "NbDocuments", "CA_Total"])
            
        # Vérifier d'abord si la table/vue existe
        cursor = conn.cursor()
        try:
            # Vérifier si le schéma OData existe
            cursor.execute("SELECT SCHEMA_ID('OData')")
            schema_id = cursor.fetchone()[0]
            
            if not schema_id:
                st.warning("Le schéma OData n'existe pas dans la base de données.")
                return pd.DataFrame(columns=["CodeClient", "NbDocuments", "CA_Total"])
                
            # Vérifier si la vue LineCustomerInvoiceList existe
            cursor.execute("SELECT OBJECT_ID('OData.LineCustomerInvoiceList')")
            view_id = cursor.fetchone()[0]
            
            if not view_id:
                st.warning("La vue OData.LineCustomerInvoiceList n'existe pas dans la base de données.")
                return pd.DataFrame(columns=["CodeClient", "NbDocuments", "CA_Total"])
                
            # Utiliser la vue LineCustomerInvoiceList pour les données clients
            query = f"""
            SELECT 
                LineDocumentThirdPartyAccount AS CodeClient,
                COUNT(DISTINCT LineDocumentCode) as NbDocuments,
                SUM(LineDocumentAmount) as CA_Total
            FROM [OData].[LineCustomerInvoiceList]
            WHERE 
                YEAR(LineDocumentDocumentDate) = {year}
                AND LineDocumentIndex = '0'  -- Uniquement les lignes avec index = 0 (pas les avenants)
            GROUP BY LineDocumentThirdPartyAccount
            ORDER BY SUM(LineDocumentAmount) DESC
            """
            
            df = pd.read_sql(query, conn)
            return df.head(limit)
            
        except pymssql.Error as e:
            st.error(f"Erreur lors de la vérification/exécution de la requête: {e}")
            return pd.DataFrame(columns=["CodeClient", "NbDocuments", "CA_Total"])
    except pymssql.Error as e:
        st.error(f"Erreur de connexion a la base de donnees : {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

# Cache désactivé temporairement
def get_monthly_sales_detail(entity_filter="Groupe ITA", year=None, month=None):
    """
    Calcule le chiffre d'affaires journalier pour un mois spécifique en utilisant les vues OData
    
    Cette fonction:
    1. Accepte une année et un mois spécifiques (utilise le mois en cours par défaut)
    2. Calcule le CA pour chaque jour de ce mois
    3. Filtre sur LineDocumentCompany pour l'entité et sur codes 70*
    4. Retourne un DataFrame avec CA journalier et CA cumulé
    
    Utilisé dans: dashboard.py -> fonction plot_current_month_tracking
    Affiché dans: Graphique "Suivi du CA – Mois en cours"
    """
    conn = None
    try:
        if year is None:
            year = datetime.now().year
        
        if month is None:
            month = datetime.now().month
            
        conn = get_connection()
        if not conn:
            st.error("Impossible de se connecter à la base de données.")
            return pd.DataFrame({"jour": [], "CA_jour": [], "CA_Cumule": [], "NbFactures": []})
        
        # Vérifier qu'on est bien connecté à PMI
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME()")
        current_db = cursor.fetchone()[0]
        
        if current_db != 'PMI':
            try:
                cursor.execute("USE PMI")
                
            except pymssql.Error as e:
                st.error(f"Erreur lors du changement vers la base PMI: {e}")
                return pd.DataFrame({"jour": [], "CA_jour": [], "CA_Cumule": [], "NbFactures": []})
        
        # Vérifier si la vue existe
        try:
            cursor.execute("SELECT OBJECT_ID('OData.LineCustomerInvoiceList')")
            view_id = cursor.fetchone()[0]
            
            # OData.LineCustomerInvoiceList n'existe probablement pas
            # Utiliser directement PFACCLI comme source de données fiable
            cursor.execute("SELECT OBJECT_ID('dbo.PFACCLI')")
            table_id = cursor.fetchone()[0]
            
            if not table_id:
                st.warning("La table PFACCLI n'existe pas. Impossible de récupérer les données.")
                return pd.DataFrame({"jour": [], "CA_jour": [], "CA_Cumule": [], "NbFactures": []})
            
            # Utiliser PFACCLI comme source de données avec les bonnes colonnes
            # et filtrer sur les codes 70 pour le chiffre d'affaires
            query = f"""
            SELECT 
                DAY(CAST(PFCJDATE AS DATETIME)) as jour,
                SUM(PFCNMT) as CA_jour,
                COUNT(DISTINCT PFKTFACTUR) as NbFactures
            FROM dbo.PFACCLI
            WHERE 
                YEAR(CAST(PFCJDATE AS DATETIME)) = {year}
                AND MONTH(CAST(PFCJDATE AS DATETIME)) = {month}
                AND (PFITCPT LIKE '70%' OR (PFITCPT LIKE '79%' AND PFITCPT != '7910000000' AND PFITCPT != '7083000000'))
            GROUP BY DAY(CAST(PFCJDATE AS DATETIME))
            ORDER BY jour
            """
            
            
            df = pd.read_sql(query, conn)
            
            if df.empty:
                st.warning(f"Aucune donnée disponible pour {month}/{year}.")
                return pd.DataFrame({"jour": [], "CA_jour": [], "CA_Cumule": [], "NbFactures": []})
                
            
        except pymssql.Error as e:
            st.error(f"Erreur lors de la vérification/exécution de la requête: {e}")
            return pd.DataFrame({"jour": [], "CA_jour": [], "CA_Cumule": [], "NbFactures": []})
        
        # Si pas de données, renvoyer un DataFrame vide avec la structure attendue
        if df.empty:
            return pd.DataFrame({"jour": [], "CA_jour": [], "CA_Cumule": [], "NbFactures": []})
            
        # Calculer le CA cumulé jour après jour
        # Ex: Si CA_jour = [100, 200, 150], alors CA_Cumule = [100, 300, 450]
        # Cela permet d'afficher la progression du CA au fil du mois
        df["CA_Cumule"] = df["CA_jour"].cumsum()
        
        return df
        
    except pymssql.Error as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        return pd.DataFrame({"jour": [], "CA_jour": [], "CA_Cumule": [], "NbFactures": []})
    finally:
        if conn:
            conn.close()

# Fonction pour récupérer les entrées de commande
def get_order_entries(limit=20):
    """Récupère les entrées de commande avec index 0 (pas les avenants)"""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            st.error("Impossible de se connecter à la base de données.")
            return pd.DataFrame()
        
        # Vérifier qu'on est bien connecté à PMI
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME()")
        current_db = cursor.fetchone()[0]
        
        if current_db != 'PMI':
            st.warning(f"Connecté à la base {current_db} au lieu de PMI. Tentative de changement de base...")
            try:
                cursor.execute("USE PMI")
                
            except pymssql.Error as e:
                st.error(f"Erreur lors du changement vers la base PMI: {e}")
                return pd.DataFrame()
        
        try:
            # Rechercher les entrées de commande avec index = 0
            query = f"""
            SELECT TOP {limit}
                LineDocumentCode, 
                LineDocumentLineCode,
                LineDocumentIndex,
                LineDocumentDocumentDate,
                LineDocumentAmount,
                LineDocumentQuantity,
                LineDocumentItemCode,
                LineDocumentItemDescriptionOne,
                LineDocumentThirdPartyAccount
            FROM OData.LineProjectedCustomerOrderList
            WHERE LineDocumentIndex = '0'  -- Uniquement les lignes avec index = 0 (pas les avenants)
            ORDER BY LineDocumentDocumentDate DESC
            """
            
            df = pd.read_sql(query, conn)
            return df
        except pymssql.Error as e:
            st.error(f"Erreur lors de l'accès aux entrées de commande: {e}")
            return pd.DataFrame()
    except pymssql.Error as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

# Cache désactivé temporairement
def get_forecast_data():
    """Charge les données prévisionnelles depuis un fichier CSV"""
    today = datetime.now()
    forecast_data = {}
    
    try:
        # Charger les données depuis le fichier CSV
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'forecast_data.csv')
        if os.path.exists(csv_path):
            df_forecast = pd.read_csv(csv_path)
            
            # Normaliser les noms de colonnes pour gérer les différentes versions possibles
            df_columns = df_forecast.columns.str.lower()
            year_col = next((col for col in df_columns if col in ['annee', 'année', 'year', 'an']), None)
            month_col = next((col for col in df_columns if col in ['mois', 'month']), None)
            amount_col = next((col for col in df_columns if col in ['montant', 'amount', 'valeur', 'ca']), None)
            
            if year_col and month_col and amount_col:
                # Construire un dictionnaire pour un accès facile aux données
                for _, row in df_forecast.iterrows():
                    year = int(row[year_col])
                    month = int(row[month_col])
                    
                    if year not in forecast_data:
                        forecast_data[year] = {}
                    
                    forecast_data[year][month] = float(row[amount_col])
                
                
            else:
                st.warning("Colonnes manquantes dans le fichier CSV.")
        else:
            st.warning("Le fichier CSV n'existe pas.")
        
        # En cas d'absence de données, retourner un dictionnaire vide
        if not forecast_data:
            st.warning("Aucune donnée prévisionnelle disponible.")
            
        return forecast_data
    except Exception as e:
        st.error(f"Erreur lors du chargement des données prévisionnelles : {e}")
        return {}
