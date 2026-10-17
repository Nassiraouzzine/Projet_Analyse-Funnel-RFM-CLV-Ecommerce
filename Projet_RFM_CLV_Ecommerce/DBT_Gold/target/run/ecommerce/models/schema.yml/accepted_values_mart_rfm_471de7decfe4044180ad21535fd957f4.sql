
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        rfm_segment as value_field,
        count(*) as n_records

    from "gold"."main"."mart_rfm"
    group by rfm_segment

)

select *
from all_values
where value_field not in (
    'Champions','Loyal Customers','Potential Loyalists','New Customers','At Risk','Hibernating','Lost'
)



  
  
      
    ) dbt_internal_test