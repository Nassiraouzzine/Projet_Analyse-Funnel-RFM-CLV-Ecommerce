
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select m_score
from "gold"."main"."mart_rfm"
where m_score is null



  
  
      
    ) dbt_internal_test