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
from {{ ref('stg_returns') }}
