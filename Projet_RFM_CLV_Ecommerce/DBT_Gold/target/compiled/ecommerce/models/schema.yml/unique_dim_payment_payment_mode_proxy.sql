
    
    

select
    payment_mode_proxy as unique_field,
    count(*) as n_records

from "gold"."main"."dim_payment"
where payment_mode_proxy is not null
group by payment_mode_proxy
having count(*) > 1


