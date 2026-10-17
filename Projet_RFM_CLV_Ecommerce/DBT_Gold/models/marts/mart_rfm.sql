
-- ============================================================
-- mart_rfm : Segmentation RFM — ST2
-- 1 ligne = 1 client avec scores R, F, M et segment nommé
-- ============================================================

with reference_date as (
    -- Date de référence = lendemain de la dernière transaction
    select max(invoice_date) + interval '1 day' as ref_date
    from fact_transactions
),

rfm_raw as (
    -- Calcul des 3 métriques brutes par client
    select
        t.customer_id,
        c.country,
        -- Récence : nb de jours depuis le dernier achat
        datediff('day', max(t.invoice_date), r.ref_date)   as recency_days,
        -- Fréquence : nb de factures distinctes
        count(distinct t.invoice_no)                        as frequency,
        -- Montant : CA total généré
        round(sum(t.line_revenue), 2)                       as monetary
    from fact_transactions t
    left join dim_customer  c using (customer_id)
    cross join reference_date r
    group by t.customer_id, c.country, r.ref_date
),

rfm_scores as (
    -- Scoring 1→5 par quintile (5 = meilleur)
    select
        customer_id,
        country,
        recency_days,
        frequency,
        monetary,
        -- R : score inversé (récent = 5)
        ntile(5) over (order by recency_days desc)   as r_score,
        -- F : score direct (fréquent = 5)
        ntile(5) over (order by frequency asc)       as f_score,
        -- M : score direct (gros CA = 5)
        ntile(5) over (order by monetary asc)        as m_score
    from rfm_raw
),

rfm_segmented as (
    select
        customer_id,
        country,
        recency_days,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        -- Score composite RFM
        round((r_score + f_score + m_score) / 3.0, 2)  as rfm_score,
        -- Segmentation nommée selon grille CDC
        case
            when r_score >= 4 and f_score >= 4 and m_score >= 4
                then 'Champions'
            when f_score >= 3 and m_score >= 3
                then 'Loyal Customers'
            when r_score >= 3 and f_score <= 2
                then 'Potential Loyalists'
            when r_score >= 4 and f_score = 1
                then 'New Customers'
            when r_score <= 2 and f_score >= 3
                then 'At Risk'
            when r_score <= 2 and f_score <= 2 and m_score >= 2
                then 'Hibernating'
            else 'Lost'
        end as rfm_segment
    from rfm_scores
)

select * from rfm_segmented
order by rfm_score desc
