
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select monetary
from "gold"."main"."mart_rfm"
where monetary is null



  
  
      
    ) dbt_internal_test