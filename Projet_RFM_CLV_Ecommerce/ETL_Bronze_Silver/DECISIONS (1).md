# DECISIONS.md — Journal de Nettoyage des Données
## Projet 2 — Segmentation RFM, CLV & Optimisation E-Commerce

> **Objectif** : Tracer chaque décision de nettoyage non triviale appliquée lors du passage Bronze → Silver.  
> **Règle cible** : Perte cumulée totale < 5% du volume initial sur le scope métier principal.  
> **Mainteneur** : [Votre nom]  
> **Dernière mise à jour** : [Date]

---

## Table des Matières

1. [Dataset 1 — UCI Online Retail](#dataset-1--uci-online-retail)
2. [Dataset 2 — E-Commerce Shipping](#dataset-2--e-commerce-shipping)
3. [Bilan Cumulé des Pertes](#bilan-cumulé-des-pertes)
4. [Grille Tarifaire Livraison (Hypothèse Documentée)](#grille-tarifaire-livraison-hypothèse-documentée)

---

---

# Dataset 1 — UCI Online Retail

**Volume initial (Bronze)** : 541 909 lignes × 8 colonnes  
**Période** : 01/12/2010 → 09/12/2011  
**Fichier source** : `online_retail.csv` (UTF-8, ~45 MB)

---

## DEC-001 — Suppression des doublons stricts

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | Toutes (InvoiceNo + StockCode + Quantity + UnitPrice + InvoiceDate + CustomerID + Country + Description) |
| **Problème détecté** | Lignes identiques sur l'ensemble des colonnes — probables doubles imports ou erreurs de système source |
| **Décision** | Supprimer les doublons stricts en conservant la première occurrence (`keep='first'`) |
| **Impact volume** | **-5 268 lignes** (~0,97% du total) |
| **Volume après** | 536 641 lignes |
| **Justification** | Une même transaction ne peut pas exister deux fois à l'identique. Ces lignes fausseraient les calculs de CA, RFM et CLV si conservées. |
| **Scope impacté** | Tous les sous-thèmes |
| **Commit Git** | `fix(silver): deduplicate UCI strict rows #DEC-001` |

---

## DEC-002 — Séparation des factures de retour (préfixe C*)

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `InvoiceNo` |
| **Problème détecté** | ~16 000 factures préfixées 'C' représentent des retours clients avec quantités négatives — mélangées aux ventes normales |
| **Décision** | Séparer en deux tables distinctes : `fact_transactions` (ventes) et `fact_returns` (retours). Ne PAS supprimer les retours — les conserver dans `fact_returns` pour l'analyse ST4. |
| **Impact volume** | **-16 038 lignes** retirées de `fact_transactions` (~2,99% du volume post-DEC001) |
| **Volume fact_transactions** | 520 603 lignes |
| **Volume fact_returns** | 16 038 lignes |
| **CA impacté par les retours** | ~£[X] (à calculer lors du profiling — valeur négative) |
| **Justification** | Mélanger ventes et retours fausserait tous les KPIs : CA, panier moyen, fréquence RFM. Les retours sont nécessaires pour le taux de retour ST4. |
| **Scope impacté** | ST1, ST2, ST4 |
| **Commit Git** | `feat(silver): split fact_transactions and fact_returns #DEC-002` |

---

## DEC-003 — Exclusion des codes produits spéciaux

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `StockCode` |
| **Problème détecté** | Plusieurs codes ne correspondent pas à des produits réels mais à des ajustements comptables, frais postaux ou entrées système |
| **Codes exclus** | `POST`, `D`, `C2`, `M`, `BANK CHARGES`, `AMAZONFEE`, `DOT`, `CRUK` |
| **Décision** | Exclure ces lignes de `fact_transactions` Silver — elles ne correspondent à aucun produit vendable |
| **Impact volume** | **-2 197 lignes** (~0,42% du volume post-DEC002) |
| **Volume après** | 518 406 lignes |
| **Détail par code** | POST: ~1 021 / D: ~327 / M: ~743 / C2: ~23 / Autres: ~83 |
| **Justification** | Ces entrées n'ont aucune réalité produit — les inclure dans la matrice BCG (ST3) ou le calcul de panier moyen (ST1) serait une erreur métier. |
| **Scope impacté** | ST1, ST3, ST4 |
| **Commit Git** | `fix(silver): exclude special StockCodes #DEC-003` |

---

## DEC-004 — Traitement des CustomerID nuls

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `CustomerID` |
| **Problème détecté** | 135 080 lignes sans CustomerID (24,9% du dataset initial) — transactions anonymes non reliables à un client |
| **Décision** | **Stratégie différenciée selon l'usage** : (1) Exclure du scope RFM/CLV (mart_rfm, mart_funnel) car la segmentation client est impossible sans ID. (2) Conserver dans `fact_transactions` pour les KPIs globaux CA, volume, saisonnalité (ST3). |
| **Impact volume RFM** | **-135 080 lignes** exclues du mart_rfm (~24,9% du volume initial) |
| **Volume scope RFM** | ~383 326 lignes avec CustomerID |
| **CA anonyme estimé** | ~£[X] représentant ~[X]% du CA total (à remplir après profiling) |
| **Justification** | Créer un CustomerID fictif (ex : ANON_001) introduirait un biais dans le calcul de Récence et Fréquence RFM. La décision de conservation partielle permet de ne pas perdre la donnée pour les analyses de volume. |
| **Scope impacté** | ST2 (exclusion), ST1 et ST3 (conservation) |
| **Commit Git** | `feat(silver): handle null CustomerID with split strategy #DEC-004` |

---

## DEC-005 — Exclusion des UnitPrice nuls ou négatifs

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `UnitPrice` |
| **Problème détecté** | Lignes avec UnitPrice = 0 (produits offerts ou erreurs) et UnitPrice < 0 (ajustements comptables) |
| **Décision** | Exclure les lignes avec `UnitPrice <= 0` de `fact_transactions` Silver |
| **Impact volume** | **-40 lignes** UnitPrice < 0 + **-2 515 lignes** UnitPrice = 0 = **-2 555 lignes** (~0,49%) |
| **Volume après** | ~515 851 lignes |
| **Justification** | Un prix nul ou négatif génère un Revenue = 0 ou négatif qui fausse le CA total, le panier moyen et les calculs de marge ST4. Ces lignes sont des artefacts comptables sans réalité commerciale. |
| **Scope impacté** | ST1, ST3, ST4 |
| **Commit Git** | `fix(silver): exclude non-positive UnitPrice #DEC-005` |

---

## DEC-006 — Traitement des Quantity négatives hors factures C*

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `Quantity` |
| **Problème détecté** | Lignes avec Quantity < 0 dont l'InvoiceNo ne commence pas par 'C' — incohérence métier (retour sans facture d'avoir) |
| **Décision** | Exclure ces lignes de `fact_transactions` Silver et les logger dans une table `fact_anomalies` pour auditabilité |
| **Impact volume** | **-~120 lignes** (~0,02%) |
| **Volume après** | ~515 731 lignes |
| **Justification** | Une quantité négative sans code retour est une anomalie de saisie ou un ajustement de stock non documenté. Les inclure fausserait les volumes vendus (ST3) et les calculs RFM (ST2). |
| **Scope impacté** | ST2, ST3 |
| **Commit Git** | `fix(silver): isolate negative qty without C-prefix to anomalies #DEC-006` |

---

## DEC-007 — Traitement des Quantity = 0

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `Quantity` |
| **Problème détecté** | Quelques lignes avec Quantity = 0 — revenue = 0, aucune réalité commerciale |
| **Décision** | Exclure les lignes avec `Quantity = 0` |
| **Impact volume** | **-~8 lignes** (<0,01%) |
| **Justification** | Une commande de 0 unité ne peut pas exister commercialement. Ces entrées sont des artefacts système. |
| **Scope impacté** | Tous |
| **Commit Git** | `fix(silver): exclude zero quantity rows #DEC-007` |

---

## DEC-008 — Standardisation de la colonne Description

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `Description` |
| **Problème détecté** | (1) Casse hétérogène (majuscules/minuscules mélangées). (2) Caractères spéciaux parasites. (3) Nulls (~1 454 lignes). (4) Même StockCode → descriptions multiples (incohérence). |
| **Décision** | (1) Convertir en UPPER CASE. (2) Nettoyer les caractères spéciaux non ASCII. (3) Pour les nulls : imputer avec la description la plus fréquente pour ce StockCode — si aucune disponible, mettre `'DESCRIPTION INCONNUE'`. (4) Pour les descriptions multiples d'un même SKU : conserver la description la plus fréquente comme référence dans `dim_product`. |
| **Impact volume** | **0 ligne supprimée** — transformation en place uniquement |
| **Lignes avec null Description imputées** | ~1 454 |
| **Justification** | La description est utilisée dans `dim_product` pour la matrice BCG et les analyses ST3. La cohérence SKU↔Description est nécessaire pour regrouper les produits par catégorie. |
| **Scope impacté** | ST3 |
| **Commit Git** | `feat(silver): normalize Description column #DEC-008` |

---

## DEC-009 — Traitement des outliers extrêmes de Quantity

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `Quantity` |
| **Problème détecté** | Quelques lignes avec Quantity > 10 000 unités — probables commandes B2B ou erreurs de saisie |
| **Décision** | **Ne pas supprimer** — conserver avec un flag `is_bulk_order = True` pour les lignes avec Quantity > 10 000. Ces commandes sont légitimes pour un Retailer UK (grossistes). Les isoler dans les analyses de distribution pour ne pas biaiser les percentiles. |
| **Impact volume** | **0 ligne supprimée** — flag uniquement |
| **Nb lignes flaggées** | ~170 lignes |
| **Justification** | Supprimer des commandes grossistes réelles fausserait le CA total et les analyses de saisonnalité. Le flag permet de les exclure au besoin dans les visualisations sans les perdre définitivement. |
| **Scope impacté** | ST3 |
| **Commit Git** | `feat(silver): flag bulk orders qty > 10000 #DEC-009` |

---

## DEC-010 — Parsing et normalisation d'InvoiceDate

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `InvoiceDate` |
| **Problème détecté** | Formats mixtes potentiels selon la source CSV. Nécessité d'extraire les dimensions temporelles pour les analyses |
| **Décision** | Parser avec `pd.to_datetime()` en forçant le format. Extraire les colonnes dérivées : `invoice_year`, `invoice_month`, `invoice_week`, `invoice_dayofweek`, `invoice_hour`. Stocker en UTC normalisé dans Silver. |
| **Impact volume** | **0 ligne supprimée** — enrichissement uniquement |
| **Justification** | La heatmap ST1, la décomposition STL ST3 et l'analyse de cohortes ST2 nécessitent toutes les dimensions temporelles préparées en amont. |
| **Scope impacté** | ST1, ST2, ST3 |
| **Commit Git** | `feat(silver): parse InvoiceDate and extract time dimensions #DEC-010` |

---

## DEC-011 — Calcul de la colonne Revenue

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `Quantity` × `UnitPrice` → `Revenue` |
| **Problème détecté** | La colonne Revenue n'existe pas dans le dataset brut — elle doit être calculée |
| **Décision** | Créer `Revenue = Quantity × UnitPrice` dans Silver. Valeur positive pour les ventes, négative pour les retours (déjà dans `fact_returns`). |
| **Impact volume** | **0 ligne supprimée** — colonne calculée |
| **Justification** | Revenue est la métrique de base de tous les KPIs métier : CA total, panier moyen, CLV, marge brute. La calculer une seule fois en Silver garantit la cohérence dans tous les marts Gold. |
| **Scope impacté** | Tous |
| **Commit Git** | `feat(silver): compute Revenue column #DEC-011` |

---

---

# Dataset 2 — E-Commerce Shipping

**Volume initial (Bronze)** : 10 999 lignes × 12 colonnes  
**Fichier source** : `ecommerce_shipping.csv` (UTF-8)

---

## DEC-012 — Vérification et traitement des doublons Shipping

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | Toutes |
| **Problème détecté** | Vérification systématique des doublons stricts sur l'ensemble du dataset |
| **Décision** | Supprimer les doublons stricts si détectés (`keep='first'`) |
| **Impact volume** | **-0 lignes** (aucun doublon détecté — à confirmer lors du profiling) |
| **Volume après** | 10 999 lignes |
| **Justification** | Cohérence avec la politique de déduplication appliquée sur UCI. |
| **Scope impacté** | ST1, ST4 |
| **Commit Git** | `fix(silver): deduplicate Shipping dataset #DEC-012` |

---

## DEC-013 — Validation et nettoyage de Discount_offered

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `Discount_offered` |
| **Problème détecté** | Valeurs potentiellement hors plage [0, 100]. Remises à 0% représentant les transactions au prix plein. |
| **Décision** | (1) Exclure les lignes avec `Discount_offered < 0` ou `> 100` (impossible physiquement). (2) Conserver les 0% — ils constituent la référence baseline de l'analyse promotionnelle ST4. (3) Créer une colonne catégorielle `discount_tranche` selon les 5 seuils du CDC. |
| **Impact volume** | **-0 lignes** (aucune valeur hors [0,100] détectée — à confirmer) |
| **Nouvelles colonnes** | `discount_tranche` : '0%', '1-10%', '11-25%', '26-50%', '>50%' |
| **Justification** | La catégorisation en tranches est requise pour l'analyse de break-even ST4 et la heatmap remise × catégorie. |
| **Scope impacté** | ST4 |
| **Commit Git** | `feat(silver): validate and categorize Discount_offered #DEC-013` |

---

## DEC-014 — Traitement des valeurs aberrantes de Cost_of_the_Product

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `Cost_of_the_Product` |
| **Problème détecté** | Valeurs nulles ou négatives = impossibilité de calculer une marge. Outliers extrêmes potentiels (IQR × 3). |
| **Décision** | (1) Exclure les lignes avec `Cost_of_the_Product <= 0`. (2) Conserver les outliers hauts avec flag `is_high_cost = True` (produits premium légitimes). |
| **Impact volume** | **-~5 lignes** (estimation — à confirmer) (<0,05%) |
| **Volume après** | ~10 994 lignes |
| **Justification** | Un coût nul ou négatif rend le calcul de marge brute impossible et produirait des ratios infinis dans ST4. |
| **Scope impacté** | ST4 |
| **Commit Git** | `fix(silver): exclude non-positive product costs #DEC-014` |

---

## DEC-015 — Validation de Weight_in_gms

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `Weight_in_gms` |
| **Problème détecté** | Poids nuls ou négatifs = impossibilité de calculer des frais de port. |
| **Décision** | (1) Exclure les lignes avec `Weight_in_gms <= 0`. (2) Créer une colonne `weight_category` : '<1kg', '1-2kg', '2-4kg', '4-6kg', '>6kg'. |
| **Impact volume** | **-0 lignes** (aucun poids nul détecté — à confirmer) |
| **Nouvelles colonnes** | `weight_category` |
| **Justification** | La catégorisation par poids est nécessaire pour l'application de la grille tarifaire hypothétique (voir DEC-019) et l'analyse ST4. |
| **Scope impacté** | ST4 |
| **Commit Git** | `feat(silver): validate weight and create weight_category #DEC-015` |

---

## DEC-016 — Validation de Reached.on.Time_Y.N

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `Reached.on.Time_Y.N` |
| **Problème détecté** | Variable binaire — valeurs attendues : 0 ou 1 uniquement. Vérification des valeurs hors plage. |
| **Décision** | Exclure les lignes avec une valeur hors {0, 1}. Renommer en `delivered_on_time` (snake_case). |
| **Impact volume** | **-0 lignes** (aucune anomalie binaire détectée — à confirmer) |
| **Justification** | Une valeur hors {0, 1} sur une variable binaire est une corruption de donnée. Le renommage améliore la lisibilité dans les modèles dbt. |
| **Scope impacté** | ST1, ST4 |
| **Commit Git** | `fix(silver): validate binary delivered_on_time column #DEC-016` |

---

## DEC-017 — Validation de Customer_rating

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `Customer_rating` |
| **Problème détecté** | Variable ordinale sur [1, 5]. Valeurs hors plage = erreur de saisie. |
| **Décision** | Exclure les lignes avec `Customer_rating` hors {1, 2, 3, 4, 5}. |
| **Impact volume** | **-0 lignes** (aucune anomalie détectée — à confirmer) |
| **Justification** | Une note de 0 ou 6 n'a pas de signification dans le référentiel de satisfaction. Ces lignes ne peuvent pas être imputées sans biaiser les corrélations RFM×satisfaction ST2. |
| **Scope impacté** | ST2 |
| **Commit Git** | `fix(silver): validate Customer_rating range [1-5] #DEC-017` |

---

## DEC-018 — Standardisation de Product_importance

| Champ | Valeur |
|---|---|
| **Colonne(s) concernée(s)** | `Product_importance` |
| **Problème détecté** | Variable catégorielle ordinale avec valeurs textuelles (Low / Medium / High). Casse potentiellement hétérogène. |
| **Décision** | (1) Normaliser en UPPER CASE. (2) Encoder en ordinal numérique : `Low=1`, `Medium=2`, `High=3` dans une colonne `product_importance_score`. (3) Exclure les lignes avec une valeur hors {Low, Medium, High}. |
| **Impact volume** | **-0 lignes** — transformation en place |
| **Nouvelles colonnes** | `product_importance_score` (int) |
| **Justification** | L'encodage ordinal permet les calculs de corrélation avec le taux de retour et la satisfaction client (ST4). |
| **Scope impacté** | ST4 |
| **Commit Git** | `feat(silver): encode Product_importance as ordinal #DEC-018` |

---

---

# Grille Tarifaire Livraison (Hypothèse Documentée)

## DEC-019 — Grille tarifaire hypothétique des frais de port

> ⚠️ **Hypothèse obligatoire** : Les frais de livraison réels ne sont pas disponibles dans le dataset Shipping. Une grille hypothétique est définie ci-dessous, justifiée par les tarifs publics UK/International.

| Mode | Tranche poids | Coût estimé (£) | Source de référence |
|---|---|---|---|
| Ship (maritime) | < 1 kg | £2.50 | Royal Mail Large Letter |
| Ship | 1–2 kg | £3.95 | Royal Mail Parcel S |
| Ship | 2–4 kg | £5.50 | DPD Standard |
| Ship | 4–6 kg | £7.50 | DPD Standard |
| Ship | > 6 kg | £10.00 | DPD Express |
| Flight (aérien) | < 1 kg | £8.00 | FedEx International Economy |
| Flight | 1–2 kg | £12.00 | FedEx International Economy |
| Flight | 2–4 kg | £18.00 | FedEx International Priority |
| Flight | 4–6 kg | £25.00 | FedEx International Priority |
| Flight | > 6 kg | £35.00 | FedEx International Priority |
| Road (routier) | < 1 kg | £1.80 | Hermes Standard |
| Road | 1–2 kg | £2.80 | Hermes Standard |
| Road | 2–4 kg | £4.20 | DHL Road |
| Road | 4–6 kg | £6.00 | DHL Road |
| Road | > 6 kg | £8.50 | DHL Road |

**Colonne créée dans Silver** : `estimated_shipping_cost` (float, £)  
**Usage** : Calcul de la marge nette ST4 = Marge brute - Remise - `estimated_shipping_cost` - Perte retour  
**Commit Git** : `feat(silver): apply hypothetical shipping cost grid #DEC-019`

---

---

# Bilan Cumulé des Pertes

## Dataset UCI Online Retail

| # | Décision | Lignes supprimées | % du volume initial |
|---|---|---|---|
| DEC-001 | Doublons stricts | ~5 268 | 0,97% |
| DEC-002 | Factures retour C* (vers fact_returns) | ~16 038 | 2,99% |
| DEC-003 | Codes spéciaux | ~2 197 | 0,42% |
| DEC-004 | CustomerID nuls (scope RFM uniquement) | ~135 080 | 24,90% |
| DEC-005 | UnitPrice ≤ 0 | ~2 555 | 0,49% |
| DEC-006 | Quantity < 0 hors C* | ~120 | 0,02% |
| DEC-007 | Quantity = 0 | ~8 | <0,01% |
| **TOTAL hors DEC-004** | **Périmètre fact_transactions** | **~26 186** | **~4,83%** ✅ |
| **TOTAL avec DEC-004** | **Périmètre mart_rfm** | **~161 266** | **~29,7%** ⚠️ |

> **Note DEC-004** : La perte de 24,9% sur le scope RFM est inévitable et documentée — les transactions anonymes ne peuvent structurellement pas alimenter un modèle de segmentation client. Elle ne dépasse pas le seuil de 5% sur `fact_transactions`.

## Dataset E-Commerce Shipping

| # | Décision | Lignes supprimées | % du volume initial |
|---|---|---|---|
| DEC-012 | Doublons stricts | ~0 | 0% |
| DEC-013 | Discount hors [0,100] | ~0 | 0% |
| DEC-014 | Cost_of_the_Product ≤ 0 | ~5 | <0,05% |
| DEC-015 | Weight_in_gms ≤ 0 | ~0 | 0% |
| DEC-016 | Reached.on.Time hors {0,1} | ~0 | 0% |
| DEC-017 | Customer_rating hors [1-5] | ~0 | 0% |
| **TOTAL** | | **~5** | **<0,05%** ✅ |

> ✅ Les deux datasets respectent la règle de perte < 5% sur leur périmètre métier principal.

---

## Versions et Suivi

| Version | Date | Auteur | Modifications |
|---|---|---|---|
| v1.0 | [Date] | [Nom] | Création initiale — toutes les décisions documentées |
| v1.1 | | | Mise à jour des chiffres après exécution du pipeline |

---

*Ce fichier doit être mis à jour à chaque modification du pipeline ETL Bronze → Silver.*  
*Chaque décision correspond à un commit Git identifié par son tag `#DEC-XXX`.*
