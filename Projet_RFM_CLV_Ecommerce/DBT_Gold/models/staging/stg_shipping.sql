select
    order_id,
    mode_of_shipment,
    weight_gms,
    weight_category,
    delivered_on_time,
    delivery_status,
    customer_rating,
    satisfaction_label,
    prior_purchases,
    customer_care_calls,
    product_importance,
    cost_of_product,
    discount_pct,
    discount_category,
    estimated_shipping_cost,
    margin_proxy
from read_parquet('/content/drive/MyDrive/Projet_RFM_CLV_Ecommerce/Data/silver/ecommerce_shipping_silver.parquet')
