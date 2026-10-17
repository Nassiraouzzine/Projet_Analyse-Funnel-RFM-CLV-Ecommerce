
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select category_proxy
from "gold"."main"."fact_transactions"
where category_proxy is null



  
  
      
    ) dbt_internal_test