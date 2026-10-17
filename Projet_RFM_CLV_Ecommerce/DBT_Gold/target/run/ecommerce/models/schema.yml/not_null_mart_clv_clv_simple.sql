
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select clv_simple
from "gold"."main"."mart_clv"
where clv_simple is null



  
  
      
    ) dbt_internal_test