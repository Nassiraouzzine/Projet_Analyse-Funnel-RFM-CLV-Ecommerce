> Projet académique d'équipe (5 personnes), réalisé en 2026.
> **Ma contribution (Nassira Ouzzine) :** traitement des données (pipeline ETL
> Bronze → Silver dans `ETL_Bronze_Silver` et modèles dbt de la couche Gold
> dans `DBT_Gold`, avec DuckDB) et dashboard Tableau.

# 🛒 Projet PFA – Analyse Funnel, Segmentation RFM & CLV E-Commerce

## 📌 Description

Ce projet a pour objectif d'exploiter des données e-commerce afin d'identifier des opportunités d'amélioration de la performance commerciale grâce à l'analyse de données.

Le projet est structuré autour de deux volets principaux :

### ST1 – Analyse du Funnel de Conversion
- Exploration et nettoyage des données.
- Analyse des paniers abandonnés.
- Identification des points de friction dans le parcours client.
- Calcul des KPIs du funnel de conversion.
- Recommandations pour améliorer le taux de conversion.

### ST2 – Segmentation RFM & Customer Lifetime Value (CLV)
- Construction des indicateurs RFM :
  - Recency
  - Frequency
  - Monetary
- Segmentation des clients.
- Estimation du Customer Lifetime Value.
- Identification des segments à forte valeur.
- Élaboration de recommandations marketing ciblées.

---

## 👥 Membres de l'équipe

- Nassira Ouzzine
- Aicha Idaani
- Wafaa Chtakire
- Hajar Elmimouni
- Manal Lazmi

---

## Technologies utilisées

- Google Colab
- Python
- Jupyter Notebook
- Pandas
- NumPy
- DuckDB
- SQL
- dbt
- Git
- Tableau

---

## 📁 Structure du projet

```
Projet_RFM_CLV_Ecommerce/
│
├── Dashboard_PowerBI/      # Dashboards Tableau
├── Data/                   # Jeux de données brutes et préparées
├── DBT_Gold/               # Modèles dbt Gold
├── ETL_Bronze_Silver/      # Pipeline ETL Bronze → Silver
├── Notebooks/              # Analyses exploratoires et modélisation
├── Profiling/              # Rapports de data profiling (HTML)
├── rapport/                # Rapports finaux (PDF, DOCX...)
├── README.md
```

---

## Installation

Cloner le dépôt :

```bash
git clone https://github.com/Nassiraouzzine/Projet_Analyse-Funnel-RFM-CLV-Ecommerce.git
cd Projet_Analyse-Funnel-RFM-CLV-Ecommerce/Projet_RFM_CLV_Ecommerce
```

Installer les librairies :

```bash
pip install pandas numpy matplotlib jupyter duckdb
```

---

## Exécution

Lancer Jupyter Notebook :

```bash
jupyter notebook
```

Ouvrir ensuite les notebooks présents dans le dossier `Notebooks`.

---

## Résultats obtenus

### ST1
- Analyse du funnel de conversion.
- Identification des causes d'abandon.
- Recommandations d'optimisation.

### ST2
- Segmentation RFM des clients.
- Estimation du CLV.
- Priorisation des actions marketing.
- Calcul du ROI estimé des recommandations.

---

## 📈 Recommandations Business

- Programme de rétention des clients à risque.
- Mise en place d'un programme VIP pour les Champions.
- Acquisition ciblée des profils à forte valeur.
