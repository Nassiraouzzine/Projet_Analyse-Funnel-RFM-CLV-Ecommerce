
    
    

with all_values as (

    select
        r_score as value_field,
        count(*) as n_records

    from "gold"."main"."mart_rfm"
    group by r_score

)

select *
from all_values
where value_field not in (
    '1','2','3','4','5'
)


