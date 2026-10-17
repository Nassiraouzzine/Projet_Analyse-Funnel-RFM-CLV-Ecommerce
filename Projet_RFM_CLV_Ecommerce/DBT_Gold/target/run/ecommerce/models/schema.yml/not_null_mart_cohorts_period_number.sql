
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select period_number
from "gold"."main"."mart_cohorts"
where period_number is null



  
  
      
    ) dbt_internal_test