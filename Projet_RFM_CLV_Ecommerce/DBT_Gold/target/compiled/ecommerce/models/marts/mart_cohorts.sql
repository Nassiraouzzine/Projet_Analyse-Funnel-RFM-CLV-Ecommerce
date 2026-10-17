-- ============================================================
-- mart_cohorts : Rétention par cohorte d'acquisition — ST2
-- Cohorte = mois du premier achat
-- 1 ligne = 1 cohorte × 1 mois_ordre avec nb clients actifs
-- ============================================================

with first_purchase as (
    -- Mois du premier achat par client (cohorte)
    select
        customer_id,
        date_trunc('month', min(invoice_date))   as cohort_month,
        min(invoice_date)                        as first_order_date
    from fact_transactions
    group by customer_id
),

orders_with_cohort as (
    -- Joindre chaque commande à la cohorte du client
    select
        t.customer_id,
        f.cohort_month,
        date_trunc('month', t.invoice_date)       as order_month,
        -- Indice de période (0 = mois d'acquisition)
        datediff('month', f.cohort_month, date_trunc('month', t.invoice_date)) as period_number
    from fact_transactions t
    inner join first_purchase f using (customer_id)
),

cohort_size as (
    -- Taille de chaque cohorte (nb clients au mois 0)
    select
        cohort_month,
        count(distinct customer_id) as cohort_size
    from first_purchase
    group by cohort_month
),

retention_raw as (
    -- Nb de clients actifs par cohorte × période
    select
        cohort_month,
        period_number,
        count(distinct customer_id) as active_customers
    from orders_with_cohort
    group by cohort_month, period_number
)

select
    r.cohort_month,
    strftime(r.cohort_month, '%Y-%m')               as cohort_label,
    r.period_number,
    r.active_customers,
    s.cohort_size,
    -- Taux de rétention en %
    round(100.0 * r.active_customers / s.cohort_size, 1)  as retention_rate
from retention_raw r
inner join cohort_size s using (cohort_month)
order by r.cohort_month, r.period_number