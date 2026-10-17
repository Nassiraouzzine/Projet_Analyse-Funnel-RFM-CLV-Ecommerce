
-- ============================================================
-- mart_clv : Customer Lifetime Value simplifiée — ST2
-- CLV = Panier moyen × Fréquence annuelle × Durée relation
-- 1 ligne = 1 client avec CLV et comparaison CAC estimé
-- ============================================================

with base as (
    -- Agrégation par client
    select
        t.customer_id,
        -- Panier moyen par commande
        round(sum(t.line_revenue) / count(distinct t.invoice_no), 2)    as avg_basket,
        -- Nb commandes totales
        count(distinct t.invoice_no)                                     as total_orders,
        -- CA total
        round(sum(t.line_revenue), 2)                                    as total_revenue,
        -- Durée relation en mois
        datediff('month',
            min(t.invoice_date),
            max(t.invoice_date)
        ) + 1                                                            as relation_months,
        -- Première et dernière commande
        min(t.invoice_date)                                              as first_order_date,
        max(t.invoice_date)                                              as last_order_date
    from fact_transactions t
    group by t.customer_id
),

clv_computed as (
    select
        b.customer_id,
        b.avg_basket,
        b.total_orders,
        b.total_revenue,
        b.relation_months,
        b.first_order_date,
        b.last_order_date,
        -- Fréquence annuelle estimée
        round(b.total_orders / greatest(b.relation_months / 12.0, 1), 2)    as annual_frequency,
        -- Durée relation estimée (en années) — cap à 3 ans
        least(round(b.relation_months / 12.0, 2), 3.0)                      as relation_years,
        -- CLV simplifiée
        round(
            b.avg_basket
            * round(b.total_orders / greatest(b.relation_months / 12.0, 1), 2)
            * least(round(b.relation_months / 12.0, 2), 3.0),
        2)                                                                   as clv_simple,
        -- Coût rétention estimé (hypothèse : 10% du CA)
        round(b.total_revenue * 0.10, 2)                                     as retention_cost_est,
        -- CLV nette
        round(
            b.avg_basket
            * round(b.total_orders / greatest(b.relation_months / 12.0, 1), 2)
            * least(round(b.relation_months / 12.0, 2), 3.0)
            - (b.total_revenue * 0.10),
        2)                                                                   as clv_net
    from base b
),

with_segment as (
    -- Jointure avec le segment RFM
    select
        c.*,
        r.rfm_segment,
        r.rfm_score,
        r.r_score,
        r.f_score,
        r.m_score,
        r.recency_days,
        r.monetary,
        r.country,
        -- Catégorie CLV
        case
            when c.clv_simple >= 1000 then 'High Value'
            when c.clv_simple >= 300  then 'Medium Value'
            else                           'Low Value'
        end as clv_category
    from clv_computed c
    left join mart_rfm r using (customer_id)
)

select * from with_segment
order by clv_simple desc
