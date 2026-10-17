
    
    

with all_values as (

    select
        clv_category as value_field,
        count(*) as n_records

    from "gold"."main"."mart_clv"
    group by clv_category

)

select *
from all_values
where value_field not in (
    'High Value','Medium Value','Low Value'
)


