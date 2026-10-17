with sessions as (
    select
        customer_id,
        session_date,
        country,
        invoice_month,
        invoice_week,
        sum(line_revenue)           as basket_value,
        count(distinct invoice_no)  as nb_invoices,
        sum(quantity)               as nb_items,
        round(avg(invoice_hour), 0) as avg_hour,
        max(invoice_day_of_week)    as weekday,
        max(category_proxy)         as main_category,
        max(price_tier)             as dominant_price_tier
    from "gold"."main"."fact_transactions"
    group by customer_id, session_date, country,
             invoice_month, invoice_week
)
select
    *,
    true as is_converted,
    case
        when basket_value < 20  then 'Low (<20 GBP)'
        when basket_value < 100 then 'Medium (20-100)'
        else                         'High (>100)'
    end as basket_tier
from sessions