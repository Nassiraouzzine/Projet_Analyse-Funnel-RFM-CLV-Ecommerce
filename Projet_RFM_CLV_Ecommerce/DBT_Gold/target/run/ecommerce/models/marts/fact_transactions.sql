
  
    
    

    create  table
      "gold"."main"."fact_transactions__dbt_tmp"
  
    as (
      select
    invoice_no,
    invoice_date,
    session_date,
    invoice_year,
    invoice_month,
    invoice_week,
    invoice_day_of_week,
    invoice_hour,
    customer_id,
    stock_code,
    description,
    category_proxy,
    quantity,
    unit_price,
    price_tier,
    line_revenue,
    country
from "gold"."main"."stg_transactions"
    );
  
  