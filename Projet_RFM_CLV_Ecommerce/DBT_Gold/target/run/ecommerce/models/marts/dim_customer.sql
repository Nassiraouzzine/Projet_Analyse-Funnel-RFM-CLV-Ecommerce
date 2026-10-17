
  
    
    

    create  table
      "gold"."main"."dim_customer__dbt_tmp"
  
    as (
      select
    customer_id,
    country,
    min(session_date)              as first_purchase_date,
    max(session_date)              as last_purchase_date,
    count(distinct session_date)   as nb_active_days,
    count(distinct invoice_no)     as total_orders,
    round(sum(line_revenue), 2)    as total_revenue,
    round(avg(line_revenue), 2)    as avg_line_revenue
from "gold"."main"."fact_transactions"
group by customer_id, country
    );
  
  