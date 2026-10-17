select
    InvoiceNo                                       as invoice_no,
    InvoiceDate                                     as invoice_date,
    invoice_date_only                               as session_date,
    invoice_year,
    invoice_month,
    invoice_week,
    invoice_day_of_week,
    invoice_hour,
    CustomerID                                      as customer_id,
    StockCode                                       as stock_code,
    Description                                     as description,
    upper(split_part(trim(Description), ' ', 1))    as category_proxy,
    Quantity                                        as quantity,
    UnitPrice                                       as unit_price,
    TotalRevenue                                    as line_revenue,
    Country                                         as country,
    case
        when UnitPrice < 2   then 'Low (<2 GBP)'
        when UnitPrice < 10  then 'Medium (2-10)'
        else                      'High (>10)'
    end                                             as price_tier
from read_parquet('/content/drive/MyDrive/Projet_RFM_CLV_Ecommerce/Data/silver/online_retail_silver.parquet')
where is_identified     = true
  and is_return         = false
  and Quantity          > 0
  and is_quantity_outlier = false