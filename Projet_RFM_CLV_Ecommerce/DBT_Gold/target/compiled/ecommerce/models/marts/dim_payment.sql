-- dim_payment : proxy via mode_of_shipment (dataset Shipping)
-- Le dataset UCI Online Retail ne contient pas de mode de paiement.
-- Hypothèse documentée DEC-PAYMENT-001 : on utilise mode_of_shipment
-- comme dimension de traitement de commande, corrélée au canal d'achat.
select
    mode_of_shipment                        as payment_mode_proxy,
    COUNT(*)                                as nb_orders,
    ROUND(AVG(discount_pct), 1)             as avg_discount_pct,
    ROUND(AVG(customer_rating), 2)          as avg_satisfaction,
    ROUND(AVG(estimated_shipping_cost), 2)  as avg_shipping_cost,
    ROUND(100.0 * SUM(CASE WHEN delivered_on_time = 1 THEN 1 ELSE 0 END)
          / COUNT(*), 1)                    as pct_on_time,
    -- enrichissement métier
    case mode_of_shipment
        when 'Ship'   then 'Maritime — délai long, coût faible'
        when 'Flight' then 'Aérien — délai court, coût élevé'
        when 'Road'   then 'Routier — délai moyen, coût moyen'
    end                                     as mode_description
from "gold"."main"."stg_shipping"
group by mode_of_shipment