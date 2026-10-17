
  
    
    

    create  table
      "gold"."main"."fact_returns__dbt_tmp"
  
    as (
      select
    invoice_no,
    stock_code,
    description,
    qty_returned,
    invoice_date,
    unit_price,
    customer_id,
    country,
    revenue_lost
from "gold"."main"."stg_returns"
    );
  
  