
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select r_score
from "gold"."main"."mart_rfm"
where r_score is null



  
  
      
    ) dbt_internal_test