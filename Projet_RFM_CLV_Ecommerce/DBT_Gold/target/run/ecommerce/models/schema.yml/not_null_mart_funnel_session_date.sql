
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select session_date
from "gold"."main"."mart_funnel"
where session_date is null



  
  
      
    ) dbt_internal_test