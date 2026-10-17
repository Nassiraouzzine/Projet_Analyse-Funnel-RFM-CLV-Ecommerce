
    
    

with all_values as (

    select
        is_converted as value_field,
        count(*) as n_records

    from "gold"."main"."mart_funnel"
    group by is_converted

)

select *
from all_values
where value_field not in (
    'True'
)


