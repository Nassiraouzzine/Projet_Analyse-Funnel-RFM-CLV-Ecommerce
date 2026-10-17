
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

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



  
  
      
    ) dbt_internal_test