import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import numpy as np
from pages.db_utils import get_sales_data, get_orders_data

def display_page(entity=None):
    st.header("Analyse par Secteurs d'Activité")
    
    now = datetime.now()
    current_year = now.year
    
    # Si une entité est fournie, l'utiliser, sinon afficher le sélecteur
    if entity is None:
        entity_options = ["Groupe ITA", "ITA Moulding Process", "ITA Solutions"]
        selected_entity = st.selectbox("Sélectionner l'entité :", entity_options, index=0)
    else:
        selected_entity = entity
    
    sales_data = get_sales_data(selected_entity)
    orders_data = get_orders_data(selected_entity)
    
    if sales_data.empty:
        st.warning("Impossible de récupérer les données. Veuillez vérifier la connexion à la base de données.")
        return
    
    # KPIs pour les différents secteurs
    col1, col2, col3, col4 = st.columns(4)
    
    sectors = extract_sectors(sales_data)
    
    for i, (sector_name, sector_data) in enumerate(sectors.items()):
        with [col1, col2, col3, col4][i % 4]:
            display_sector_kpi(sector_name, sector_data['amount'], sector_data['count'])
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_sector_distribution(sectors)
    
    with col2:
        display_sector_trend(sales_data)
    
    st.markdown("---")
    
    display_sector_comparison(sales_data)

def extract_sectors(df):
    # Importer la configuration des secteurs
    from pages.secteurs_config import SECTEURS, SECTEUR_KEYWORDS, CLIENT_SECTORS
    
    # Initialiser tous les secteurs avec des valeurs à 0
    sectors = {secteur_name: {'amount': 0, 'count': 0} for secteur_name in SECTEURS.values()}
    
    if 'LineDocumentItemDescriptionOne' in df.columns:
        for _, row in df.iterrows():
            desc = str(row['LineDocumentItemDescriptionOne']).lower() if pd.notnull(row['LineDocumentItemDescriptionOne']) else ""
            amount = row['LineDocumentAmount']
            
            # Vérifier d'abord si le client correspond à un secteur connu
            classified = False
            
            # 1. Essayer de classer par nom de client connu
            for client_name, sector_code in CLIENT_SECTORS.items():
                if client_name.lower() in desc.lower():
                    sector_name = SECTEURS[sector_code]
                    sectors[sector_name]['amount'] += amount
                    sectors[sector_name]['count'] += 1
                    classified = True
                    break
            
            # 2. Si pas de correspondance client, essayer par mots-clés
            if not classified:
                for sector_code, keywords in SECTEUR_KEYWORDS.items():
                    if any(keyword.lower() in desc.lower() for keyword in keywords):
                        sector_name = SECTEURS[sector_code]
                        sectors[sector_name]['amount'] += amount
                        sectors[sector_name]['count'] += 1
                        classified = True
                        break
            
            # 3. Si toujours pas classifié, mettre dans DIVERS
            if not classified:
                sectors[SECTEURS["11"]]['amount'] += amount
                sectors[SECTEURS["11"]]['count'] += 1
    else:
        # Si les données ne contiennent pas la colonne description, mettre tout dans DIVERS
        total_amount = df['LineDocumentAmount'].sum() if not df.empty else 0
        total_count = len(df)
        sectors[SECTEURS["11"]]['amount'] = total_amount
        sectors[SECTEURS["11"]]['count'] = total_count
    
    return sectors

def display_sector_kpi(sector_name, amount, count):
    st.metric(
        label=sector_name,
        value=f"{amount:,.0f} €",
        delta=f"{count} document(s)"
    )

def display_sector_distribution(sectors):
    st.subheader("Répartition du CA par Secteur")
    
    sector_data = pd.DataFrame({
        'Secteur': list(sectors.keys()),
        'Montant': [sector['amount'] for sector in sectors.values()]
    })
    
    chart = alt.Chart(sector_data).mark_arc().encode(
        theta=alt.Theta(field="Montant", type="quantitative"),
        color=alt.Color(field="Secteur", type="nominal", 
                      scale=alt.Scale(domain=list(sectors.keys()), 
                                    range=['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'])),
        tooltip=[
            alt.Tooltip('Secteur:N', title='Secteur'),
            alt.Tooltip('Montant:Q', title='Montant', format=',.0f')
        ]
    ).properties(height=300)
    
    st.altair_chart(chart, use_container_width=True)

def display_sector_trend(df):
    st.subheader("Évolution par Secteur")
    
    if 'LineDocumentItemDescriptionOne' in df.columns:
        df['year'] = df['LineDocumentDocumentDate'].dt.year
        df['month'] = df['LineDocumentDocumentDate'].dt.month
        df['yearmonth'] = df['LineDocumentDocumentDate'].dt.strftime('%Y-%m')
        
        # Simplification: on ne regarde que les 12 derniers mois
        now = datetime.now()
        last_year = datetime(now.year - 1, now.month, 1)
        df_recent = df[df['LineDocumentDocumentDate'] >= last_year]
        
        # Extraction des secteurs
        df_recent['Secteur'] = 'Autre'
        
        for _, row in df_recent.iterrows():
            desc = str(row['LineDocumentItemDescriptionOne']).lower() if pd.notnull(row['LineDocumentItemDescriptionOne']) else ""
            
            if 'bureau' in desc or 'siège' in desc or 'chaise' in desc:
                df_recent.at[_, 'Secteur'] = 'Mobilier Bureau'
            elif 'médical' in desc or 'santé' in desc or 'hôpital' in desc:
                df_recent.at[_, 'Secteur'] = 'Médical'
            elif 'spectacle' in desc or 'scénique' in desc or 'théâtre' in desc:
                df_recent.at[_, 'Secteur'] = 'Spectacle'
            elif 'nautisme' in desc or 'bateau' in desc or 'naval' in desc:
                df_recent.at[_, 'Secteur'] = 'Nautisme'
        
        # Agrégation par mois et secteur
        monthly_sector = df_recent.groupby(['yearmonth', 'Secteur'])['LineDocumentAmount'].sum().reset_index()
        
        # Création du graphique
        chart = alt.Chart(monthly_sector).mark_area().encode(
            x=alt.X('yearmonth:T', axis=alt.Axis(title='Période', labelAngle=45)),
            y=alt.Y('LineDocumentAmount:Q', axis=alt.Axis(title='Montant (€)'), stack='normalize'),
            color=alt.Color('Secteur:N', scale=alt.Scale(domain=['Mobilier Bureau', 'Médical', 'Spectacle', 'Nautisme', 'Autre'], 
                                                     range=['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'])),
            tooltip=[
                alt.Tooltip('yearmonth:T', title='Période'),
                alt.Tooltip('Secteur:N', title='Secteur'),
                alt.Tooltip('LineDocumentAmount:Q', title='Montant', format=',.0f')
            ]
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Pas de données disponibles pour le secteur automobile")


def display_sector_comparison(df):
    st.subheader("Comparaison des Secteurs")
    
    if 'LineDocumentItemDescriptionOne' in df.columns:
        df['year'] = df['LineDocumentDocumentDate'].dt.year
        
        # Extraction des secteurs pour les 3 dernières années
        now = datetime.now()
        current_year = now.year
        df_years = df[df['year'] >= current_year - 2]
        
        # Classification par secteur
        df_years['Secteur'] = 'Autre'
        
        for _, row in df_years.iterrows():
            desc = str(row['LineDocumentItemDescriptionOne']).lower() if pd.notnull(row['LineDocumentItemDescriptionOne']) else ""
            
            if 'bureau' in desc or 'siège' in desc or 'chaise' in desc:
                df_years.at[_, 'Secteur'] = 'Mobilier Bureau'
            elif 'médical' in desc or 'santé' in desc or 'hôpital' in desc:
                df_years.at[_, 'Secteur'] = 'Médical'
            elif 'spectacle' in desc or 'scénique' in desc or 'théâtre' in desc:
                df_years.at[_, 'Secteur'] = 'Spectacle'
            elif 'nautisme' in desc or 'bateau' in desc or 'naval' in desc:
                df_years.at[_, 'Secteur'] = 'Nautisme'
        
        # Agrégation par année et secteur
        yearly_sector = df_years.groupby(['year', 'Secteur'])['LineDocumentAmount'].sum().reset_index()
        
        # Création du graphique
        chart = alt.Chart(yearly_sector).mark_bar().encode(
            x=alt.X('Secteur:N', axis=alt.Axis(title='Secteur')),
            y=alt.Y('LineDocumentAmount:Q', axis=alt.Axis(title='Montant (€)')),
            color=alt.Color('year:N', scale=alt.Scale(scheme='blues')),
            tooltip=[
                alt.Tooltip('year:N', title='Année'),
                alt.Tooltip('Secteur:N', title='Secteur'),
                alt.Tooltip('LineDocumentAmount:Q', title='Montant', format=',.0f')
            ]
        ).properties(height=400)
        
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Données secteurs insuffisantes pour afficher le graphique")
