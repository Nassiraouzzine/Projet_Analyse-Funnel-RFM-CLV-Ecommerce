
  
  create view "gold"."main"."stg_returns__dbt_tmp" as (
    select
    InvoiceNo               as invoice_no,
    StockCode               as stock_code,
    Description             as description,
    abs(Quantity)           as qty_returned,
    InvoiceDate             as invoice_date,
    UnitPrice               as unit_price,
    CustomerID              as customer_id,
    Country                 as country,
    abs(TotalRevenue)       as revenue_lost
from read_parquet('/content/drive/MyDrive/Projet_RFM_CLV_Ecommerce/Data/silver/fact_returns.parquet')
where CustomerID is not null
  );
