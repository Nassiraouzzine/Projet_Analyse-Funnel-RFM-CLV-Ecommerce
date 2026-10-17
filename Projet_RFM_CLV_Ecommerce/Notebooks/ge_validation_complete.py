"""
Great Expectations — Validation complète Silver
================================================
Valide les 3 fichiers Parquet Silver :
  1. fact_transactions  (online_retail_silver.parquet)
  2. fact_returns        (fact_returns.parquet)
  3. ecommerce_shipping  (ecommerce_shipping_silver.parquet)
Génère ge_validation_report.html à la fin.

Usage dans Google Colab :
  %run ge_validation_complete.py
"""

# ── 0. Installation automatique ───────────────────────────────────────────────
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "great-expectations", "-q"],
               check=False)

# ── 1. Imports ────────────────────────────────────────────────────────────────
import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path

import great_expectations as gx
import great_expectations.expectations as gxe
from great_expectations.core.expectation_suite import ExpectationSuite

# ══════════════════════════════════════════════════════════════════════════════
# CHEMINS — adaptez ici si nécessaire
# ══════════════════════════════════════════════════════════════════════════════
BASE = "/content/drive/MyDrive/Projet_RFM_CLV_Ecommerce/Data/silver"

PATHS = {
    "UCI Online Retail"    : f"{BASE}/online_retail_silver.parquet",
    "Fact Returns"         : f"{BASE}/fact_returns.parquet",
    "E-Commerce Shipping"  : f"{BASE}/ecommerce_shipping_silver.parquet",
}

# ══════════════════════════════════════════════════════════════════════════════
# HELPER : exécute une liste d'expectations sur un DataFrame
# ══════════════════════════════════════════════════════════════════════════════
_suite_counter = 0

def run_validation(dataset_name, df, expectations_with_labels):
    global _suite_counter
    _suite_counter += 1

    context    = gx.get_context(mode="ephemeral")
    suite      = context.suites.add(ExpectationSuite(name=f"suite_{_suite_counter}"))
    datasource = context.data_sources.add_pandas(name=f"src_{_suite_counter}")
    asset      = datasource.add_dataframe_asset(name=f"asset_{_suite_counter}")
    batch_def  = asset.add_batch_definition_whole_dataframe(f"batch_{_suite_counter}")
    batch      = batch_def.get_batch(batch_parameters={"dataframe": df})

    results, passed, failed, failed_list = [], 0, 0, []

    for label, exp in expectations_with_labels:
        try:
            ok = batch.validate(exp).success
        except Exception:
            ok = False
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status}  {label}")
        if ok: passed += 1
        else:
            failed += 1
            failed_list.append(label)
        results.append({"rule": label, "expectation": type(exp).__name__, "success": ok})

    total  = passed + failed
    pct_ok = passed / total * 100
    verdict = "✅ 100 % PASS" if failed == 0 else f"❌ {failed} règle(s) en échec"
    print(f"\n  → {passed}/{total} PASS ({pct_ok:.0f}%)  |  {verdict}\n")

    return {
        "dataset"    : dataset_name,
        "run_at"     : datetime.now().isoformat(),
        "total_rows" : len(df),
        "total_rules": total,
        "passed"     : passed,
        "failed"     : failed,
        "pass_rate"  : round(pct_ok, 2),
        "overall"    : "PASS" if failed == 0 else "FAIL",
        "details"    : results,
    }

# ══════════════════════════════════════════════════════════════════════════════
# DATASET 1 — UCI Online Retail (fact_transactions)
# DEC-001 à DEC-011
# ══════════════════════════════════════════════════════════════════════════════
def validate_uci(df):
    SPECIAL_CODES = ['POST','D','C2','M','BANK CHARGES','AMAZONFEE','DOT','CRUK']
    return [
        ("Schéma — 18 colonnes ordonnées",
         gxe.ExpectTableColumnsToMatchOrderedList(column_list=[
             "InvoiceNo","InvoiceDate","invoice_year","invoice_month","invoice_week",
             "invoice_day_of_week","invoice_hour","invoice_date_only",
             "CustomerID","is_identified","StockCode","Description",
             "Quantity","UnitPrice","TotalRevenue","Country",
             "is_return","is_quantity_outlier"
         ])),
        ("Volume — entre 1 et 600 000 lignes",
         gxe.ExpectTableRowCountToBeBetween(min_value=1, max_value=600_000)),
        # DEC-001
        ("DEC-001 — InvoiceNo non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="InvoiceNo")),
        ("DEC-001 — StockCode non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="StockCode")),
        # DEC-002
        ("DEC-002 — Aucune facture retour C* dans fact_transactions",
         gxe.ExpectColumnValuesToNotMatchRegex(column="InvoiceNo", regex=r"^C")),
        # DEC-003
        ("DEC-003 — Aucun code produit spécial",
         gxe.ExpectColumnValuesToNotBeInSet(column="StockCode", value_set=SPECIAL_CODES)),
        # DEC-004
        ("DEC-004 — is_identified non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="is_identified")),
        ("DEC-004 — is_identified ∈ {True, False}",
         gxe.ExpectColumnValuesToBeInSet(column="is_identified", value_set=[True, False])),
        # DEC-005
        ("DEC-005 — UnitPrice non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="UnitPrice")),
        ("DEC-005 — UnitPrice > 0",
         gxe.ExpectColumnValuesToBeBetween(column="UnitPrice", min_value=0.01)),
        # DEC-006 / DEC-007
        ("DEC-006/007 — Quantity non nulle",
         gxe.ExpectColumnValuesToNotBeNull(column="Quantity")),
        ("DEC-006/007 — Quantity ≥ 1 (pas de zéro ni négatif)",
         gxe.ExpectColumnValuesToBeBetween(column="Quantity", min_value=1)),
        # DEC-008
        ("DEC-008 — Description non nulle",
         gxe.ExpectColumnValuesToNotBeNull(column="Description")),
        ("DEC-008 — Description en UPPER ASCII",
         gxe.ExpectColumnValuesToMatchRegex(
             column="Description", regex=r"^[A-Z0-9 .,'\-\/\(\)&\+!%*#@$:;?_]+$")),
        # DEC-009
        ("DEC-009 — is_quantity_outlier ∈ {True, False}",
         gxe.ExpectColumnValuesToBeInSet(column="is_quantity_outlier", value_set=[True, False])),
        # DEC-010
        ("DEC-010 — InvoiceDate non nulle",
         gxe.ExpectColumnValuesToNotBeNull(column="InvoiceDate")),
        ("DEC-010 — invoice_year ∈ [2010, 2011]",
         gxe.ExpectColumnValuesToBeBetween(column="invoice_year", min_value=2010, max_value=2011)),
        ("DEC-010 — invoice_month ∈ [1, 12]",
         gxe.ExpectColumnValuesToBeBetween(column="invoice_month", min_value=1, max_value=12)),
        ("DEC-010 — invoice_day_of_week ∈ [0, 6]",
         gxe.ExpectColumnValuesToBeBetween(column="invoice_day_of_week", min_value=0, max_value=6)),
        ("DEC-010 — invoice_hour ∈ [0, 23]",
         gxe.ExpectColumnValuesToBeBetween(column="invoice_hour", min_value=0, max_value=23)),
        # DEC-011
        ("DEC-011 — TotalRevenue > 0",
         gxe.ExpectColumnValuesToBeBetween(column="TotalRevenue", min_value=0.01)),
        ("DEC-011 — is_return = False dans fact_transactions",
         gxe.ExpectColumnValuesToBeInSet(column="is_return", value_set=[False])),
        # Intégrité
        ("Intégrité — Country non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="Country")),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# DATASET 2 — Fact Returns
# Règles inverses / complémentaires à DEC-002
# ══════════════════════════════════════════════════════════════════════════════
def validate_returns(df):
    return [
        ("Schéma — colonnes présentes",
         gxe.ExpectTableColumnsToMatchSet(column_set=[
             "InvoiceNo","InvoiceDate","CustomerID","StockCode",
             "Description","Quantity","UnitPrice","Country","TotalRevenue"
         ], exact_match=False)),
        ("Volume — au moins 1 retour",
         gxe.ExpectTableRowCountToBeBetween(min_value=1, max_value=100_000)),
        # Toutes les factures doivent commencer par C
        ("Retours — InvoiceNo commence par C*",
         gxe.ExpectColumnValuesToMatchRegex(column="InvoiceNo", regex=r"^C")),
        # Quantity négative (c'est le propre d'un retour)
        ("Retours — Quantity < 0",
         gxe.ExpectColumnValuesToBeBetween(column="Quantity", max_value=-1)),
        # TotalRevenue négatif
        ("Retours — TotalRevenue < 0",
         gxe.ExpectColumnValuesToBeBetween(column="TotalRevenue", max_value=-0.01)),
        # CustomerID présent (les retours sont toujours identifiés)
        ("Retours — CustomerID non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="CustomerID")),
        # UnitPrice > 0 (le prix unitaire reste positif même sur un retour)
        ("Retours — UnitPrice > 0",
         gxe.ExpectColumnValuesToBeBetween(column="UnitPrice", min_value=0.01)),
        # InvoiceDate non nulle
        ("Retours — InvoiceDate non nulle",
         gxe.ExpectColumnValuesToNotBeNull(column="InvoiceDate")),
        # Country non nul
        ("Retours — Country non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="Country")),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# DATASET 3 — E-Commerce Shipping
# DEC-012 à DEC-019
# ══════════════════════════════════════════════════════════════════════════════
def validate_shipping(df):
    required = [c for c in [
        "order_id","warehouse_block","mode_of_shipment","weight_gms","weight_category",
        "delivered_on_time","delivery_status","gender","customer_rating","satisfaction_label",
        "prior_purchases","customer_care_calls","product_importance","product_importance_score",
        "is_high_cost","cost_of_product","discount_pct","discount_category",
        "discount_amount_proxy","estimated_shipping_cost","net_cost_after_discount","margin_proxy"
    ] if c in df.columns]
    return [
        ("Schéma — colonnes ordonnées",
         gxe.ExpectTableColumnsToMatchOrderedList(column_list=required)),
        ("Volume — entre 1 et 15 000 lignes",
         gxe.ExpectTableRowCountToBeBetween(min_value=1, max_value=15_000)),
        # DEC-012
        ("DEC-012 — order_id non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="order_id")),
        ("DEC-012 — order_id unique (pas de doublons)",
         gxe.ExpectColumnValuesToBeUnique(column="order_id")),
        # DEC-013
        ("DEC-013 — discount_pct non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="discount_pct")),
        ("DEC-013 — discount_pct ∈ [0, 100]",
         gxe.ExpectColumnValuesToBeBetween(column="discount_pct", min_value=0, max_value=100)),
        ("DEC-013 — discount_category valide",
         gxe.ExpectColumnValuesToBeInSet(column="discount_category",
             value_set=["0%_prix_plein","1-10%_leger","11-25%_significatif",
                        "26-50%_fort",">50%_liquidation"])),
        # DEC-014
        ("DEC-014 — cost_of_product non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="cost_of_product")),
        ("DEC-014 — cost_of_product > 0",
         gxe.ExpectColumnValuesToBeBetween(column="cost_of_product", min_value=0.01)),
        ("DEC-014 — is_high_cost booléen",
         gxe.ExpectColumnValuesToBeInSet(column="is_high_cost", value_set=[True, False])),
        # DEC-015
        ("DEC-015 — weight_gms non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="weight_gms")),
        ("DEC-015 — weight_gms > 0",
         gxe.ExpectColumnValuesToBeBetween(column="weight_gms", min_value=1)),
        ("DEC-015 — weight_category valide",
         gxe.ExpectColumnValuesToBeInSet(column="weight_category",
             value_set=["<1kg","1-2kg","2-4kg","4-6kg",">6kg"])),
        # DEC-016
        ("DEC-016 — delivered_on_time non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="delivered_on_time")),
        ("DEC-016 — delivered_on_time ∈ {0, 1}",
         gxe.ExpectColumnValuesToBeInSet(column="delivered_on_time", value_set=[0, 1])),
        ("DEC-016 — delivery_status ∈ {On_Time, Late}",
         gxe.ExpectColumnValuesToBeInSet(column="delivery_status",
             value_set=["On_Time","Late"])),
        # DEC-017
        ("DEC-017 — customer_rating non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="customer_rating")),
        ("DEC-017 — customer_rating ∈ {1, 2, 3, 4, 5}",
         gxe.ExpectColumnValuesToBeInSet(column="customer_rating",
             value_set=[1, 2, 3, 4, 5])),
        # DEC-018
        ("DEC-018 — product_importance non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="product_importance")),
        ("DEC-018 — product_importance ∈ {Low, Medium, High}",
         gxe.ExpectColumnValuesToBeInSet(column="product_importance",
             value_set=["Low","Medium","High"])),
        ("DEC-018 — product_importance_score ∈ {1, 2, 3}",
         gxe.ExpectColumnValuesToBeInSet(column="product_importance_score",
             value_set=[1, 2, 3])),
        # DEC-019
        ("DEC-019 — mode_of_shipment ∈ {Ship, Flight, Road}",
         gxe.ExpectColumnValuesToBeInSet(column="mode_of_shipment",
             value_set=["Ship","Flight","Road"])),
        ("DEC-019 — estimated_shipping_cost > 0",
         gxe.ExpectColumnValuesToBeBetween(column="estimated_shipping_cost", min_value=0.01)),
        # ST4
        ("ST4 — discount_amount_proxy ≥ 0",
         gxe.ExpectColumnValuesToBeBetween(column="discount_amount_proxy", min_value=0)),
        ("ST4 — net_cost_after_discount ≥ 0",
         gxe.ExpectColumnValuesToBeBetween(column="net_cost_after_discount", min_value=0)),
        ("ST4 — margin_proxy non nul",
         gxe.ExpectColumnValuesToNotBeNull(column="margin_proxy")),
        # Intégrité
        ("Intégrité — warehouse_block ∈ {A,B,C,D,F}",
         gxe.ExpectColumnValuesToBeInSet(column="warehouse_block",
             value_set=["A","B","C","D","F"])),
        ("Intégrité — gender ∈ {M, F}",
         gxe.ExpectColumnValuesToBeInSet(column="gender", value_set=["M","F"])),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATEUR DE DONNÉES SYNTHÉTIQUES (mode démo sans fichiers Parquet)
# ══════════════════════════════════════════════════════════════════════════════
def make_uci_demo():
    np.random.seed(42)
    n = 5_000
    dates = pd.date_range("2010-12-01", "2011-12-09", periods=n)
    return pd.DataFrame({
        "InvoiceNo"           : [f"5{str(i).zfill(5)}" for i in range(n)],
        "InvoiceDate"         : dates,
        "invoice_year"        : dates.year,
        "invoice_month"       : dates.month,
        "invoice_week"        : dates.isocalendar().week.astype(int),
        "invoice_day_of_week" : dates.dayofweek,
        "invoice_hour"        : np.random.randint(6, 20, n),
        "invoice_date_only"   : [str(d.date()) for d in dates],
        "CustomerID"          : [str(10000 + i % 4000) for i in range(n)],
        "is_identified"       : np.random.choice([True, False], n, p=[0.75, 0.25]),
        "StockCode"           : [f"SKU{i % 500:04d}" for i in range(n)],
        "Description"         : ["PRODUCT DESCRIPTION"] * n,
        "Quantity"            : np.random.randint(1, 100, n).astype(float),
        "UnitPrice"           : np.round(np.random.uniform(0.01, 50.0, n), 2),
        "TotalRevenue"        : np.round(np.random.uniform(0.01, 2000.0, n), 2),
        "Country"             : np.random.choice(["United Kingdom","France","Germany"], n),
        "is_return"           : [False] * n,
        "is_quantity_outlier" : np.random.choice([True, False], n, p=[0.02, 0.98]),
    })

def make_returns_demo():
    np.random.seed(1)
    n = 500
    dates = pd.date_range("2010-12-01", "2011-12-09", periods=n)
    return pd.DataFrame({
        "InvoiceNo"    : [f"C{str(i).zfill(6)}" for i in range(n)],
        "InvoiceDate"  : dates,
        "CustomerID"   : [str(10000 + i % 4000) for i in range(n)],
        "StockCode"    : [f"SKU{i % 500:04d}" for i in range(n)],
        "Description"  : ["RETURNED ITEM"] * n,
        "Quantity"     : np.random.randint(1, 20, n).astype(float) * -1,
        "UnitPrice"    : np.round(np.random.uniform(0.01, 50.0, n), 2),
        "Country"      : np.random.choice(["United Kingdom","France","Germany"], n),
        "TotalRevenue" : np.round(np.random.uniform(0.01, 500.0, n), 2) * -1,
    })

def make_shipping_demo():
    np.random.seed(0)
    n = 10_999
    return pd.DataFrame({
        "order_id"                : list(range(1, n + 1)),
        "warehouse_block"         : np.random.choice(list("ABCDF"), n),
        "mode_of_shipment"        : np.random.choice(["Ship","Flight","Road"], n, p=[0.68,0.18,0.14]),
        "weight_gms"              : np.random.randint(1000, 7000, n),
        "weight_category"         : np.random.choice(["<1kg","1-2kg","2-4kg","4-6kg",">6kg"], n),
        "delivered_on_time"       : np.random.choice([0, 1], n),
        "delivery_status"         : np.random.choice(["On_Time","Late"], n),
        "gender"                  : np.random.choice(["M","F"], n),
        "customer_rating"         : np.random.randint(1, 6, n),
        "satisfaction_label"      : np.random.choice(
            ["Tres insatisfait","Insatisfait","Neutre","Satisfait","Tres satisfait"], n),
        "prior_purchases"         : np.random.randint(2, 8, n),
        "customer_care_calls"     : np.random.randint(1, 7, n),
        "product_importance"      : np.random.choice(["Low","Medium","High"], n),
        "product_importance_score": np.random.choice([1, 2, 3], n),
        "is_high_cost"            : np.random.choice([True, False], n, p=[0.05, 0.95]),
        "cost_of_product"         : np.random.randint(96, 308, n).astype(float),
        "discount_pct"            : np.random.randint(0, 66, n).astype(float),
        "discount_category"       : np.random.choice(
            ["0%_prix_plein","1-10%_leger","11-25%_significatif","26-50%_fort",">50%_liquidation"], n),
        "discount_amount_proxy"   : np.round(np.random.uniform(0, 80, n), 2),
        "estimated_shipping_cost" : np.round(np.random.uniform(1.8, 35.0, n), 2),
        "net_cost_after_discount" : np.round(np.random.uniform(50, 300, n), 2),
        "margin_proxy"            : np.round(np.random.uniform(-5, 280, n), 2),
    })

# ══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT DES 3 DATASETS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("  CHARGEMENT DES FICHIERS SILVER")
print("="*65)

datasets = {}
demo_fns = {
    "UCI Online Retail"   : make_uci_demo,
    "Fact Returns"        : make_returns_demo,
    "E-Commerce Shipping" : make_shipping_demo,
}

for name, path in PATHS.items():
    try:
        df = pd.read_parquet(path)
        print(f"  ✅ {name:<25} {len(df):>8,} lignes  ← {path}")
    except FileNotFoundError:
        df = demo_fns[name]()
        print(f"  ⚠️  {name:<25} {len(df):>8,} lignes  (jeu synthétique — fichier introuvable)")
    datasets[name] = df

# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION DES 3 DATASETS
# ══════════════════════════════════════════════════════════════════════════════
all_reports = []

configs = [
    ("UCI Online Retail",   validate_uci),
    ("Fact Returns",        validate_returns),
    ("E-Commerce Shipping", validate_shipping),
]

for name, build_fn in configs:
    df = datasets[name]
    print(f"\n{'='*65}")
    print(f"  VALIDATION — {name}  ({len(df):,} lignes)")
    print(f"{'='*65}\n")
    report = run_validation(name, df, build_fn(df))
    all_reports.append(report)

# ══════════════════════════════════════════════════════════════════════════════
# RAPPORT HTML
# ══════════════════════════════════════════════════════════════════════════════
total_rules  = sum(r["total_rules"] for r in all_reports)
total_passed = sum(r["passed"]      for r in all_reports)
total_failed = sum(r["failed"]      for r in all_reports)
global_pct   = total_passed / total_rules * 100
global_color = "#16a34a" if total_failed == 0 else "#dc2626"
global_label = "✅ 100 % PASS — Toutes les données Silver sont conformes" \
    if total_failed == 0 else f"❌ {total_failed} règle(s) en échec"

def badge(ok):
    return ('<span class="badge pass">✅ PASS</span>' if ok
            else '<span class="badge fail">❌ FAIL</span>')

def table_rows(details):
    rows = []
    for i, d in enumerate(details):
        bg = "" if d["success"] else ' style="background:#fff1f1"'
        rows.append(f"""
        <tr{bg}>
          <td class="num">{i+1}</td>
          <td>{d['rule']}</td>
          <td><code>{d['expectation']}</code></td>
          <td class="center">{badge(d['success'])}</td>
        </tr>""")
    return "\n".join(rows)

def dataset_card(r):
    pct   = r["pass_rate"]
    color = "#16a34a" if r["overall"] == "PASS" else "#dc2626"
    circ  = 2 * 3.14159 * 36
    arc   = round((pct / 100) * circ, 2)
    off   = round(circ * 0.25, 2)

    icons = {"UCI Online Retail": "🛒", "Fact Returns": "↩️", "E-Commerce Shipping": "🚚"}
    icon  = icons.get(r["dataset"], "📦")

    return f"""
    <section class="card">
      <div class="card-header">
        <div>
          <h2>{icon} {r['dataset']}</h2>
          <p class="meta">
            {r['run_at'][:19].replace('T',' ')} &nbsp;|&nbsp;
            {r['total_rows']:,} lignes analysées
          </p>
        </div>
        <div class="gauge-wrap">
          <svg viewBox="0 0 90 90" width="88" height="88">
            <circle cx="45" cy="45" r="36" fill="none" stroke="#e5e7eb" stroke-width="9"/>
            <circle cx="45" cy="45" r="36" fill="none"
              stroke="{color}" stroke-width="9"
              stroke-dasharray="{arc} {round(circ-arc,2)}"
              stroke-dashoffset="{off}" stroke-linecap="round"/>
            <text x="45" y="50" text-anchor="middle"
              font-size="14" font-weight="bold" fill="{color}">{int(pct)}%</text>
          </svg>
          <p class="gauge-lbl" style="color:{color}">{r['passed']}/{r['total_rules']}</p>
        </div>
      </div>
      <div class="stat-row">
        <div class="stat green"><span>{r['passed']}</span>PASS</div>
        <div class="stat {'red' if r['failed'] else 'gray'}"><span>{r['failed']}</span>FAIL</div>
        <div class="stat blue"><span>{r['total_rules']}</span>RÈGLES</div>
        <div class="stat {'green' if r['overall']=='PASS' else 'red'}">
          <span>{'✅' if r['overall']=='PASS' else '❌'}</span>VERDICT
        </div>
      </div>
      <table class="tbl">
        <thead>
          <tr><th>#</th><th>Règle de qualité</th><th>Expectation GE</th><th>Statut</th></tr>
        </thead>
        <tbody>{table_rows(r['details'])}</tbody>
      </table>
    </section>"""

DEC_LEGEND = [
    ("DEC-001","Suppression doublons stricts"),
    ("DEC-002","Séparation factures retour C*"),
    ("DEC-003","Exclusion codes produits spéciaux"),
    ("DEC-004","CustomerID nuls — flag is_identified"),
    ("DEC-005","Exclusion UnitPrice ≤ 0"),
    ("DEC-006","Quantity négatives hors C*"),
    ("DEC-007","Exclusion Quantity = 0"),
    ("DEC-008","Normalisation Description UPPER ASCII"),
    ("DEC-009","Outliers Quantity — flag IQR×3"),
    ("DEC-010","Feature Engineering temporel"),
    ("DEC-011","TotalRevenue & CustomerID normalisé"),
    ("DEC-012","Doublons Shipping — order_id unique"),
    ("DEC-013","Discount_offered ∈ [0, 100]"),
    ("DEC-014","Cost_of_the_Product > 0"),
    ("DEC-015","Weight_in_gms > 0"),
    ("DEC-016","delivered_on_time ∈ {0, 1}"),
    ("DEC-017","customer_rating ∈ {1–5}"),
    ("DEC-018","product_importance encodé ordinal"),
    ("DEC-019","Grille tarifaire livraison"),
    ("RETURNS","fact_returns — Quantity < 0 & InvoiceNo C*"),
]
legend_html = "\n".join(
    f'<div class="dec"><span class="tag">{d}</span>{t}</div>'
    for d, t in DEC_LEGEND
)

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rapport GE — Validation Silver</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     background:#f1f5f9;color:#1e293b;font-size:14px;line-height:1.5}}
.header{{background:linear-gradient(135deg,#1e3a5f,#0f4c81);
         color:#fff;padding:32px 40px 24px}}
.header h1{{font-size:22px;font-weight:700;margin-bottom:4px}}
.header .sub{{opacity:.8;font-size:12px}}
.global{{background:#fff;border-radius:12px;margin:22px 40px 0;
         padding:22px 28px;box-shadow:0 1px 4px rgba(0,0,0,.08);
         display:flex;align-items:center;gap:24px;flex-wrap:wrap}}
.verdict{{font-size:18px;font-weight:700;color:{global_color};flex:1}}
.gstats{{display:flex;gap:18px;flex-wrap:wrap}}
.gs{{text-align:center}}
.gs .n{{font-size:24px;font-weight:800;color:#0f4c81}}
.gs .l{{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#64748b}}
.card{{background:#fff;border-radius:12px;margin:18px 40px;
       padding:22px 28px;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
.card-header{{display:flex;justify-content:space-between;
              align-items:flex-start;margin-bottom:16px;gap:12px;flex-wrap:wrap}}
.card-header h2{{font-size:16px;font-weight:700;color:#0f172a}}
.meta{{font-size:11px;color:#64748b;margin-top:3px}}
.gauge-wrap{{text-align:center}}
.gauge-lbl{{font-size:11px;font-weight:600;margin-top:2px}}
.stat-row{{display:flex;gap:10px;margin-bottom:18px;flex-wrap:wrap}}
.stat{{flex:1;min-width:65px;padding:10px;border-radius:8px;
       text-align:center;font-size:10px;text-transform:uppercase;letter-spacing:.05em}}
.stat span{{display:block;font-size:20px;font-weight:800}}
.green{{background:#f0fdf4;color:#16a34a}}
.red{{background:#fef2f2;color:#dc2626}}
.gray{{background:#f8fafc;color:#64748b}}
.blue{{background:#eff6ff;color:#2563eb}}
.tbl{{width:100%;border-collapse:collapse;font-size:13px}}
.tbl th{{background:#f8fafc;text-align:left;padding:8px 12px;
         font-size:11px;text-transform:uppercase;letter-spacing:.05em;
         color:#64748b;border-bottom:2px solid #e2e8f0}}
.tbl td{{padding:7px 12px;border-bottom:1px solid #f1f5f9;vertical-align:middle}}
.tbl tr:last-child td{{border-bottom:none}}
.tbl tr:hover td{{background:#f8fafc!important}}
.num{{color:#94a3b8;font-size:12px;width:30px}}
.center{{text-align:center}}
code{{background:#f1f5f9;padding:2px 6px;border-radius:4px;
      font-size:11px;font-family:'SF Mono','Fira Code',monospace;color:#334155}}
.badge{{display:inline-block;padding:2px 9px;border-radius:20px;
        font-size:11px;font-weight:700}}
.pass{{background:#f0fdf4;color:#16a34a}}
.fail{{background:#fef2f2;color:#dc2626}}
.legend{{background:#fff;border-radius:12px;margin:18px 40px;
         padding:20px 28px;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
.legend h3{{font-size:13px;font-weight:700;margin-bottom:12px;color:#0f172a}}
.legend-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:7px}}
.dec{{background:#f8fafc;border-radius:6px;padding:5px 9px;
      font-size:12px;display:flex;gap:8px;align-items:center}}
.tag{{background:#0f4c81;color:#fff;border-radius:4px;
      padding:1px 6px;font-size:10px;font-weight:700;white-space:nowrap}}
.footer{{text-align:center;color:#94a3b8;font-size:12px;padding:20px 40px 28px}}
</style>
</head>
<body>
<header class="header">
  <h1>📊 Rapport de Validation Great Expectations — Silver Layer</h1>
  <p class="sub">
    Pipeline ETL Bronze → Silver &nbsp;|&nbsp;
    Projet RFM, CLV &amp; Optimisation E-Commerce &nbsp;|&nbsp;
    Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
  </p>
</header>

<div class="global">
  <div class="verdict">{global_label}</div>
  <div class="gstats">
    <div class="gs"><div class="n">{total_rules}</div><div class="l">Règles</div></div>
    <div class="gs"><div class="n" style="color:#16a34a">{total_passed}</div><div class="l">PASS</div></div>
    <div class="gs"><div class="n" style="color:{'#dc2626' if total_failed else '#94a3b8'}">{total_failed}</div><div class="l">FAIL</div></div>
    <div class="gs"><div class="n">{int(global_pct)}%</div><div class="l">Conformité</div></div>
    <div class="gs"><div class="n">3</div><div class="l">Datasets</div></div>
  </div>
</div>

{''.join(dataset_card(r) for r in all_reports)}

<div class="legend">
  <h3>📋 Décisions ETL couvertes (DEC-001 à DEC-019 + Retours)</h3>
  <div class="legend-grid">{legend_html}</div>
</div>

<footer class="footer">
  Great Expectations v{gx.__version__} &nbsp;·&nbsp;
  ge_validation_complete.py &nbsp;·&nbsp;
  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</footer>
</body>
</html>"""

out = Path("ge_validation_report.html")
out.write_text(html, encoding="utf-8")

# ══════════════════════════════════════════════════════════════════════════════
# RÉSUMÉ FINAL
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("  RÉSUMÉ GLOBAL")
print("="*65)
for r in all_reports:
    v = "✅ PASS" if r["overall"] == "PASS" else "❌ FAIL"
    print(f"  {v}  {r['dataset']:<25} {r['passed']}/{r['total_rules']} règles")
print(f"\n  Total : {total_passed}/{total_rules} PASS ({int(global_pct)}%)")
print(f"  Verdict : {global_label}")
print(f"\n  📄 Rapport HTML : ge_validation_report.html")
print("="*65)

# Téléchargement automatique dans Colab
try:
    from google.colab import files
    files.download("ge_validation_report.html")
    print("  ⬇️  Téléchargement du rapport lancé...")
except ImportError:
    pass  # Hors Colab, le fichier est simplement dans le répertoire courant
