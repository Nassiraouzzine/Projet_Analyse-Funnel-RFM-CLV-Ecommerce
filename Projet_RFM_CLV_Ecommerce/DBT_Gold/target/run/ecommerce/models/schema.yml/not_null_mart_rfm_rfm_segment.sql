
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select rfm_segment
from "gold"."main"."mart_rfm"
where rfm_segment is null



  
  
      
    ) dbt_internal_test