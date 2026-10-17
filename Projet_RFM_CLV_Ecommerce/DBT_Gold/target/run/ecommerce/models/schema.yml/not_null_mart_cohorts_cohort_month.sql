
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select cohort_month
from "gold"."main"."mart_cohorts"
where cohort_month is null



  
  
      
    ) dbt_internal_test